"""DataFrame helpers and CSV upload utilities for Reprompt."""

from __future__ import annotations

import json
import logging
from typing import List, TYPE_CHECKING, Any

from .generated.models import PlaceJobResult, BatchJob

if TYPE_CHECKING:
    import pandas as pd

    PANDAS_AVAILABLE = True
else:
    try:
        import pandas as pd

        PANDAS_AVAILABLE = True
    except ImportError:
        pd = None
        PANDAS_AVAILABLE = False

# Note: CSV upload functionality removed - focusing on read-only operations

logger = logging.getLogger(__name__)


# DataFrame serialization helpers
def batches_to_dataframe(batches: List[BatchJob]) -> Any:
    """
    Convert a list of BatchJob objects to a pandas DataFrame.

    Args:
        batches: List of BatchJob objects from the API

    Returns:
        pd.DataFrame with flattened batch data

    Raises:
        ImportError: If pandas is not installed
    """
    if not PANDAS_AVAILABLE:
        raise ImportError("pandas is required for DataFrame conversion. Install with: pip install pandas")

    if not batches:
        return pd.DataFrame()

    # Convert BatchJob objects to flattened dictionaries
    data = []
    for batch in batches:
        # Work directly with the BatchJob model
        flattened = _flatten_batch_job(batch)
        data.append(flattened)

    return pd.DataFrame(data)


def jobs_to_dataframe(
    jobs: List[PlaceJobResult],
    include_inputs: bool = True,
    include_reasoning: bool = True,
    include_confidence: bool = True,
    include_batch: bool = True,
    include_not_run: bool = False,
) -> Any:
    """
    Convert a list of PlaceJobResult objects to a pandas DataFrame with flattened structure.

    Args:
        jobs: List of PlaceJobResult objects from the API
        include_inputs: Include input fields (default: True)
        include_reasoning: Include reasoning fields (default: True)
        include_confidence: Include confidence score fields (default: True)
        include_batch: Include batch_id field (default: True)
        include_not_run: Include columns with all None/NaN values (default: False)

    Returns:
        pd.DataFrame with flattened job data

    Raises:
        ImportError: If pandas is not installed
    """
    if not PANDAS_AVAILABLE:
        raise ImportError("pandas is required for DataFrame conversion. Install with: pip install pandas")

    if not jobs:
        return pd.DataFrame()

    # Convert PlaceJobResult objects to flattened dictionaries
    data = []
    for job in jobs:
        # We know job is a PlaceJobResult, work with it directly
        flattened = _flatten_place_job_result(
            job,
            include_inputs=include_inputs,
            include_reasoning=include_reasoning,
            include_confidence=include_confidence,
            include_batch=include_batch,
        )
        data.append(flattened)

    df = pd.DataFrame(data)

    # Apply include_not_run filtering if requested
    if not include_not_run:
        df = _remove_null_columns(df)

    return df


def _remove_null_columns(df: Any) -> Any:
    """Remove columns that contain only None/NaN values."""
    if df.empty:
        return df

    # Find columns that are all null (None or NaN)
    null_columns = []
    for col in df.columns:
        if df[col].isnull().all():
            null_columns.append(col)

    # Drop null columns
    if null_columns:
        df = df.drop(columns=null_columns)

    return df


def _flatten_batch_job(batch: BatchJob) -> dict:
    """Flatten BatchJob model structure for DataFrame format."""
    flattened = {}

    # Only include batch_id and batch_name
    flattened["batch_id"] = batch.id
    flattened["batch_name"] = batch.batch_name

    return flattened


def _flatten_place_job_result(  # pylint: disable=too-many-locals,too-many-branches
    job: PlaceJobResult,
    include_inputs: bool = True,
    include_reasoning: bool = True,
    include_confidence: bool = True,
    include_batch: bool = True,  # pylint: disable=unused-argument
) -> dict:
    """Flatten PlaceJobResult structure for DataFrame format with selective field inclusion."""

    # Create a sentinel for unset values
    class UNSET:  # pylint: disable=too-few-public-methods
        pass

    flattened = {}

    # Basic job info - directly access typed attributes
    flattened["place_id"] = job.place_id
    flattened["status"] = job.status

    # Handle inputs with dot notation prefix
    if include_inputs and job.inputs:
        # Only include the core fields, ignore additional/extra fields
        if hasattr(job.inputs, "model_dump"):
            inputs_dict = job.inputs.model_dump(exclude_unset=True, mode="json")
            # Filter out standard UniversalPlace fields only
            core_fields = {"type", "input_type", "name", "full_address", "latitude", "longitude"}
            for key, value in inputs_dict.items():
                if key in core_fields:
                    flattened[f"inputs.{key}"] = value
        else:
            # Fallback for dict inputs
            inputs_dict = job.inputs if isinstance(job.inputs, dict) else {}
            for key, value in inputs_dict.items():
                flattened[f"inputs.{key}"] = value

    # Handle outputs with dot notation prefix
    # Handle outputs - it's a dict in the new models
    outputs = job.outputs if isinstance(job.outputs, dict) else {}
    if outputs:
        for key, value in outputs.items():
            # For nested dicts, keep the nested structure but with dot prefix
            if isinstance(value, dict):
                for sub_key, sub_value in value.items():
                    flattened[f"outputs.{key}_{sub_key}"] = (
                        sub_value if not isinstance(sub_value, (dict, list)) else json.dumps(sub_value)
                    )
            elif isinstance(value, list):
                flattened[f"outputs.{key}"] = json.dumps(value)
            else:
                flattened[f"outputs.{key}"] = value

    # Handle reasoning with dot notation prefix
    if include_reasoning and job.reasoning:
        reasoning_dict = job.reasoning if isinstance(job.reasoning, dict) else {}
        if "additional_properties" in reasoning_dict:
            reasoning_dict = reasoning_dict["additional_properties"]
        # Add reasoning for each field with dot notation
        for key, value in reasoning_dict.items():
            flattened[f"reasoning.{key}"] = value if not isinstance(value, (dict, list)) else json.dumps(value)

    # Handle confidence_scores with dot notation prefix
    if include_confidence and job.confidence_scores is not None and not isinstance(job.confidence_scores, type(UNSET)):
        if hasattr(job.confidence_scores, "model_dump"):
            confidence_dict = job.confidence_scores.model_dump(mode="json")
        else:
            confidence_dict = {}
        if "additional_properties" in confidence_dict:
            confidence_dict = confidence_dict["additional_properties"]
        # Add confidence for each field with dot notation
        for key, value in confidence_dict.items():
            flattened[f"confidence.{key}"] = value if not isinstance(value, (dict, list)) else json.dumps(value)

    # Handle job_metadata
    if job.job_metadata:
        if hasattr(job.job_metadata, "model_dump"):
            # Use model_dump with mode='json' to handle datetime serialization
            metadata_dict = job.job_metadata.model_dump(mode="json")
        else:
            metadata_dict = {}
        flattened["job_metadata"] = json.dumps(metadata_dict)

    return flattened


# CSV upload functionality removed - focusing on read-only operations
