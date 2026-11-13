import logging
import traceback
from typing import Dict, Any, Optional
import pandas as pd
from sqlalchemy.orm import Session

from backend.app.db.session import SessionLocal
from backend.app.models.all_models import Dataset, DatasetVersion, SemanticModel, DashboardSpec
from backend.app.services.dataset_service import DatasetService
from backend.app.services.profiling import profile_dataset, calculate_data_quality_score
from backend.app.services.semantic_service import SemanticService
from backend.app.services.cleaning import CleaningService
from backend.app.services.dashboard_generator import DashboardGenerator
from backend.app.services.insight_engine import InsightEngine
from backend.app.jobs.queue import JobManager

logger = logging.getLogger("insightforge.pipeline")

class PipelineService:
    """
    Autonomous one-click pipeline for InsightForge AI:
    Ingest -> Profile -> Classify -> Auto-Clean -> Build Semantic Layer -> Generate Dashboard -> Rank Insights.
    
    Resilience Guarantee:
    A failure in any individual step is marked as 'skipped' with a recorded reason,
    allowing downstream steps to continue with available data rather than killing the job.
    """

    @classmethod
    def run_auto_pipeline(
        cls,
        dataset_id: str,
        job_id: Optional[str] = None,
        workspace_id: Optional[str] = None
    ) -> Dict[str, Any]:
        db = SessionLocal()
        step_logs = []
        partial_kpis = []
        pipeline_result = {
            "dataset_id": dataset_id,
            "job_id": job_id,
            "status": "completed",
            "step_logs": step_logs,
            "kpi_cards": [],
            "dashboard_id": None,
            "insights_count": 0,
            "cleaning_summary": {}
        }

        try:
            dataset, df = DatasetService.get_dataset_df(db, dataset_id)
            initial_df = df.copy()
            cleaned_df = initial_df.copy()
            cleaning_summary = {}

            # STEP 1: Ingest & Columnar Verification (15%)
            if job_id:
                JobManager.update_job_progress(
                    job_id, 15,
                    f"Reading dataset '{dataset.name}' ({len(initial_df)} rows, {len(initial_df.columns)} columns)...",
                    status="running"
                )
            step_logs.append({"step": "Ingest", "status": "completed", "details": f"{len(initial_df)} rows loaded."})

            # STEP 2: Profile & Health Check (30%)
            profile_data = {}
            try:
                if job_id:
                    JobManager.update_job_progress(
                        job_id, 30,
                        "Profiling column distributions, types, and calculating initial Data Quality Score...",
                        status="running"
                    )
                profile_data = profile_dataset(initial_df)
                step_logs.append({
                    "step": "Profile",
                    "status": "completed",
                    "initial_quality_score": profile_data.get("quality_score", {}).get("overall", 100.0)
                })
            except Exception as e:
                logger.warning(f"Pipeline Step 2 (Profile) skipped due to error: {e}")
                step_logs.append({"step": "Profile", "status": "skipped", "reason": str(e)})

            # STEP 3: Classify Domain & Column Roles (45%)
            sem_dict = {}
            try:
                if job_id:
                    JobManager.update_job_progress(
                        job_id, 45,
                        "Classifying business domain, dimensions, and metric expressions...",
                        status="running"
                    )
                sem_dict = SemanticService.build_semantic_layer(initial_df)
                step_logs.append({
                    "step": "Classify",
                    "status": "completed",
                    "detected_domain": sem_dict.get("domain", "general")
                })
            except Exception as e:
                logger.warning(f"Pipeline Step 3 (Classify) skipped due to error: {e}")
                sem_dict = {"metrics": [], "dimensions": [], "time_grains": [], "domain": "general"}
                step_logs.append({"step": "Classify", "status": "skipped", "reason": str(e)})

            # STEP 4: Auto-Clean with Safe Defaults (60%)
            # Applies only low-risk safe fixes (trim whitespace, fix data types, parse dates, strip currency and %,
            # Indian numbers, remove blank rows/columns, subtotal rows, casing, duplicates).
            # Flags risky items as suggestions.
            try:
                if job_id:
                    JobManager.update_job_progress(
                        job_id, 60,
                        "Applying safe fixes: dates, currency symbols, whitespace, and subtotal rows...",
                        status="running"
                    )
                cleaned_df, cleaning_summary = CleaningService.auto_clean_safe_defaults(initial_df)
                
                # Save cleaned data as version 2 (immutable step)
                if len(cleaning_summary.get("applied_steps", [])) > 0:
                    summary_text = f"Auto-cleaned {cleaning_summary.get('issues_fixed_count', 0)} issues with safe defaults."
                    new_version = DatasetService.create_new_version(
                        db, dataset, cleaned_df, summary_text
                    )
                    dataset.current_version = new_version.version_num
                    dataset.row_count = len(cleaned_df)
                    dataset.col_count = len(cleaned_df.columns)
                    db.commit()

                step_logs.append({
                    "step": "Auto-Clean",
                    "status": "completed",
                    "issues_fixed": cleaning_summary.get("issues_fixed_count", 0),
                    "score_before": cleaning_summary.get("score_before", {}).get("overall", 100),
                    "score_after": cleaning_summary.get("score_after", {}).get("overall", 100),
                    "applied_steps": cleaning_summary.get("applied_steps", []),
                    "suggestions": cleaning_summary.get("suggestions", [])
                })
            except Exception as e:
                logger.warning(f"Pipeline Step 4 (Auto-Clean) skipped due to error: {e}")
                cleaned_df = initial_df
                step_logs.append({"step": "Auto-Clean", "status": "skipped", "reason": str(e)})

            # STEP 5: Build Unified Semantic Layer (75%)
            try:
                if job_id:
                    JobManager.update_job_progress(
                        job_id, 75,
                        "Building Unified Semantic Layer with grounded metric formulas...",
                        status="running"
                    )
                # Re-build semantic layer on cleaned dataframe
                sem_dict = SemanticService.build_semantic_layer(cleaned_df)

                # Persist SemanticModel silently to database
                existing_sem = db.query(SemanticModel).filter(
                    SemanticModel.dataset_id == dataset.id,
                    SemanticModel.version_num == dataset.current_version
                ).first()

                if not existing_sem:
                    existing_sem = SemanticModel(
                        dataset_id=dataset.id,
                        version_num=dataset.current_version,
                        domain=sem_dict.get("domain", "general"),
                        metrics_json=sem_dict.get("metrics", []),
                        dimensions_json=sem_dict.get("dimensions", []),
                        time_grains_json=sem_dict.get("time_grains", []),
                        target_column=sem_dict.get("suggested_target"),
                        ml_task_type=sem_dict.get("suggested_ml_task", "regression"),
                        confidence=sem_dict.get("confidence", 0.9)
                    )
                    db.add(existing_sem)
                else:
                    existing_sem.domain = sem_dict.get("domain", "general")
                    existing_sem.metrics_json = sem_dict.get("metrics", [])
                    existing_sem.dimensions_json = sem_dict.get("dimensions", [])
                    existing_sem.time_grains_json = sem_dict.get("time_grains", [])
                db.commit()

                step_logs.append({
                    "step": "Semantic Layer",
                    "status": "completed",
                    "metrics_count": len(sem_dict.get("metrics", [])),
                    "dimensions_count": len(sem_dict.get("dimensions", []))
                })
            except Exception as e:
                logger.warning(f"Pipeline Step 5 (Semantic Layer) skipped due to error: {e}")
                step_logs.append({"step": "Semantic Layer", "status": "skipped", "reason": str(e)})

            # STEP 6: Generate Dashboard Spec & Early Partial Results (88%)
            dash_spec = {}
            try:
                if job_id:
                    JobManager.update_job_progress(
                        job_id, 88,
                        "Generating executive dashboard and calculating key metrics...",
                        status="running"
                    )

                dash_spec = DashboardGenerator.generate_auto_dashboard(
                    cleaned_df,
                    sem_dict,
                    title=f"{dataset.name} Performance Dashboard",
                    dataset_name=dataset.name,
                    cleaning_summary=cleaning_summary
                )

                # Partial results: KPI cards available early
                partial_kpis = dash_spec.get("kpi_cards", [])
                if job_id and partial_kpis:
                    JobManager.update_job_progress(
                        job_id, 92,
                        "Key numbers ready! Synthesizing ranked insights...",
                        status="running",
                        result={"kpi_cards": partial_kpis}
                    )

                # Persist DashboardSpec to database
                existing_dash = db.query(DashboardSpec).filter(
                    DashboardSpec.dataset_id == dataset.id,
                    DashboardSpec.version_num == dataset.current_version
                ).first()

                if not existing_dash:
                    existing_dash = DashboardSpec(
                        dataset_id=dataset.id,
                        workspace_id=dataset.workspace_id,
                        name=dash_spec["title"],
                        version_num=dataset.current_version,
                        spec_json=dash_spec,
                        is_default=True
                    )
                    db.add(existing_dash)
                else:
                    existing_dash.spec_json = dash_spec
                db.commit()
                db.refresh(existing_dash)
                pipeline_result["dashboard_id"] = existing_dash.id

                step_logs.append({
                    "step": "Dashboard",
                    "status": "completed",
                    "charts_count": len(dash_spec.get("charts", [])),
                    "kpi_count": len(dash_spec.get("kpi_cards", []))
                })
            except Exception as e:
                logger.warning(f"Pipeline Step 6 (Dashboard) skipped due to error: {e}")
                step_logs.append({"step": "Dashboard", "status": "skipped", "reason": str(e)})

            # STEP 7: Rank Insights & Suggested Chatbot Questions (100%)
            insights_list = []
            try:
                if job_id:
                    JobManager.update_job_progress(
                        job_id, 95,
                        "Discovering statistical anomalies, segments, and ranking top insights...",
                        status="running"
                    )

                insights_list = InsightEngine.generate_and_rank_insights(cleaned_df, sem_dict)
                top_5_insights = insights_list[:5]

                # Embed top 5 insights into the DashboardSpec so Dashboard renders them directly
                if existing_dash and "spec_json" in existing_dash.__dict__:
                    updated_spec = dict(existing_dash.spec_json)
                    updated_spec["insights"] = top_5_insights
                    existing_dash.spec_json = updated_spec
                    db.commit()

                step_logs.append({
                    "step": "Insights",
                    "status": "completed",
                    "insights_count": len(insights_list)
                })
            except Exception as e:
                logger.warning(f"Pipeline Step 7 (Insights) skipped due to error: {e}")
                step_logs.append({"step": "Insights", "status": "skipped", "reason": str(e)})

            # STEP 8: Auto-Train ML Baseline Models (98%)
            try:
                suggested_target = sem_dict.get("suggested_target")
                if suggested_target and suggested_target in cleaned_df.columns and len(cleaned_df) >= 15:
                    if job_id:
                        JobManager.update_job_progress(
                            job_id, 98,
                            f"Auto-training predictive models for '{suggested_target}'...",
                            status="running"
                        )
                    from backend.app.ml.automl import AutoMLTrainer
                    from backend.app.models.all_models import ModelMetadata
                    model_save_name = f"automl_{dataset.id}_{suggested_target}.joblib"
                    ml_res = AutoMLTrainer.train_and_evaluate(cleaned_df, suggested_target, model_save_name)
                    
                    existing_model = db.query(ModelMetadata).filter(
                        ModelMetadata.dataset_id == dataset.id,
                        ModelMetadata.target_column == suggested_target
                    ).first()
                    if not existing_model:
                        existing_model = ModelMetadata(
                            dataset_id=dataset.id,
                            name=f"AutoML {suggested_target}",
                            task_type=ml_res["task_type"],
                            target_column=suggested_target,
                            feature_names=ml_res.get("feature_names", []),
                            algorithm=ml_res.get("best_model", "Random Forest"),
                            metrics_json=ml_res.get("leaderboard", []),
                            feature_importance_json=ml_res.get("feature_importance", []),
                            model_path=ml_res.get("model_path")
                        )
                        db.add(existing_model)
                    else:
                        existing_model.metrics_json = ml_res.get("leaderboard", [])
                        existing_model.feature_importance_json = ml_res.get("feature_importance", [])
                    db.commit()
                    step_logs.append({"step": "AutoML", "status": "completed", "target": suggested_target, "best_model": ml_res.get("best_model")})
            except Exception as e:
                logger.warning(f"Pipeline Step 8 (AutoML) skipped due to error: {e}")
                step_logs.append({"step": "AutoML", "status": "skipped", "reason": str(e)})

            # Complete Job
            pipeline_result["kpi_cards"] = partial_kpis
            pipeline_result["insights_count"] = len(insights_list)
            pipeline_result["cleaning_summary"] = cleaning_summary
            pipeline_result["status"] = "completed"

            if job_id:
                JobManager.update_job_progress(
                    job_id, 100,
                    f"Analysis complete! Cleaned {cleaning_summary.get('issues_fixed_count', 0)} issues. Dashboard is ready.",
                    status="completed",
                    result=pipeline_result
                )

            return pipeline_result

        except Exception as global_err:
            logger.error(f"Global pipeline exception: {global_err}\n{traceback.format_exc()}")
            if job_id:
                JobManager.update_job_progress(
                    job_id, 100,
                    f"Pipeline finalized with partial data: {str(global_err)}",
                    status="completed",
                    result=pipeline_result,
                    error=str(global_err)
                )
            return pipeline_result
        finally:
            db.close()
