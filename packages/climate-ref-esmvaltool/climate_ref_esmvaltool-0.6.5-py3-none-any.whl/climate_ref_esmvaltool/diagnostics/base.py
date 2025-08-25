from abc import abstractmethod
from collections.abc import Iterable
from pathlib import Path
from typing import ClassVar

import pandas
import yaml
from loguru import logger

from climate_ref_core.dataset_registry import dataset_registry_manager
from climate_ref_core.datasets import ExecutionDatasetCollection, SourceDatasetType
from climate_ref_core.diagnostics import (
    CommandLineDiagnostic,
    ExecutionDefinition,
    ExecutionResult,
)
from climate_ref_core.pycmec.metric import CMECMetric, MetricCV
from climate_ref_core.pycmec.output import CMECOutput, OutputCV
from climate_ref_esmvaltool.recipe import load_recipe, prepare_climate_data
from climate_ref_esmvaltool.types import MetricBundleArgs, OutputBundleArgs, Recipe


class ESMValToolDiagnostic(CommandLineDiagnostic):
    """ESMValTool Diagnostic base class."""

    base_recipe: ClassVar[str]

    @staticmethod
    @abstractmethod
    def update_recipe(recipe: Recipe, input_files: pandas.DataFrame) -> None:
        """
        Update the base recipe for the run.

        Parameters
        ----------
        recipe:
            The base recipe to update.
        input_files:
            The dataframe describing the input files.

        """

    @staticmethod
    def format_result(
        result_dir: Path,
        execution_dataset: ExecutionDatasetCollection,
        metric_args: MetricBundleArgs,
        output_args: OutputBundleArgs,
    ) -> tuple[CMECMetric, CMECOutput]:
        """
        Update the arguments needed to create a CMEC diagnostic and output bundle.

        Parameters
        ----------
        result_dir
            Directory containing executions from an ESMValTool run.
        execution_dataset
            The diagnostic dataset used for the diagnostic execution.
        metric_args
            Generic diagnostic bundle arguments.
        output_args
            Generic output bundle arguments.

        Returns
        -------
            The arguments needed to create a CMEC diagnostic and output bundle.
        """
        return CMECMetric.model_validate(metric_args), CMECOutput.model_validate(output_args)

    def build_cmd(self, definition: ExecutionDefinition) -> Iterable[str]:
        """
        Build the command to run an ESMValTool recipe.

        Parameters
        ----------
        definition
            A description of the information needed for this execution of the diagnostic

        Returns
        -------
        :
            The result of running the diagnostic.
        """
        input_files = definition.datasets[SourceDatasetType.CMIP6].datasets
        recipe = load_recipe(self.base_recipe)
        self.update_recipe(recipe, input_files)

        recipe_path = definition.to_output_path("recipe.yml")
        with recipe_path.open("w", encoding="utf-8") as file:
            yaml.dump(recipe, file)

        climate_data = definition.to_output_path("climate_data")

        prepare_climate_data(
            definition.datasets[SourceDatasetType.CMIP6].datasets,
            climate_data_dir=climate_data,
        )

        config = {
            "drs": {
                "CMIP6": "ESGF",
                "obs4MIPs": "ESGF",
            },
            "output_dir": str(definition.to_output_path("executions")),
            "rootpath": {
                "CMIP6": str(climate_data),
                "obs4MIPs": str(climate_data),
            },
            "search_esgf": "never",
        }

        # Configure the paths to OBS/OBS6/native6 and non-compliant obs4MIPs data
        registry = dataset_registry_manager["esmvaltool"]
        data_dir = registry.abspath / "ESMValTool"  # type: ignore[attr-defined]
        if not data_dir.exists():
            logger.warning(
                "ESMValTool observational and reanalysis data is not available "
                f"in {data_dir}, you may want to run the command "
                "`ref datasets fetch-data --registry esmvaltool`."
            )
        else:
            config["drs"].update(  # type: ignore[attr-defined]
                {
                    "OBS": "default",
                    "OBS6": "default",
                    "native6": "default",
                }
            )
            config["rootpath"].update(  # type: ignore[attr-defined]
                {
                    "OBS": str(data_dir / "OBS"),
                    "OBS6": str(data_dir / "OBS"),
                    "native6": str(data_dir / "RAWOBS"),
                }
            )
            config["rootpath"]["obs4MIPs"] = [  # type: ignore[index]
                config["rootpath"]["obs4MIPs"],  # type: ignore[index]
                str(data_dir),
            ]

        config_dir = definition.to_output_path("config")
        config_dir.mkdir()
        with (config_dir / "config.yml").open("w", encoding="utf-8") as file:
            yaml.dump(config, file)

        return [
            "esmvaltool",
            "run",
            f"--config-dir={config_dir}",
            f"{recipe_path}",
        ]

    def build_execution_result(
        self,
        definition: ExecutionDefinition,
    ) -> ExecutionResult:
        """
        Build the diagnostic result after running an ESMValTool recipe.

        Parameters
        ----------
        definition
            A description of the information needed for this execution of the diagnostic

        Returns
        -------
        :
            The resulting diagnostic.
        """
        result_dir = next(definition.to_output_path("executions").glob("*"))

        metric_args = CMECMetric.create_template()
        output_args = CMECOutput.create_template()

        # Add the plots and data files
        plot_suffixes = {".png", ".jpg", ".pdf", ".ps"}
        for metadata_file in result_dir.glob("run/*/*/diagnostic_provenance.yml"):
            metadata = yaml.safe_load(metadata_file.read_text(encoding="utf-8"))
            for filename in metadata:
                caption = metadata[filename].get("caption", "")
                relative_path = definition.as_relative_path(filename)
                if relative_path.suffix in plot_suffixes:
                    key = OutputCV.PLOTS.value
                else:
                    key = OutputCV.DATA.value
                output_args[key][f"{relative_path}"] = {
                    OutputCV.FILENAME.value: f"{relative_path}",
                    OutputCV.LONG_NAME.value: caption,
                    OutputCV.DESCRIPTION.value: "",
                }

        # Add the index.html file
        index_html = f"{result_dir}/index.html"
        output_args[OutputCV.HTML.value][index_html] = {
            OutputCV.FILENAME.value: index_html,
            OutputCV.LONG_NAME.value: "Results page",
            OutputCV.DESCRIPTION.value: "Page showing the executions of the ESMValTool run.",
        }
        output_args[OutputCV.INDEX.value] = index_html

        # Add the (debug) log file
        output_args[OutputCV.PROVENANCE.value][OutputCV.LOG.value] = f"{result_dir}/run/main_log_debug.txt"

        # Update the diagnostic and output bundle with diagnostic specific executions.
        metric_bundle, output_bundle = self.format_result(
            result_dir=result_dir,
            execution_dataset=definition.datasets,
            metric_args=metric_args,
            output_args=output_args,
        )

        # Add the extra information from the groupby operations
        if len(metric_bundle.DIMENSIONS[MetricCV.JSON_STRUCTURE.value]):
            input_selectors = definition.datasets[SourceDatasetType.CMIP6].selector_dict()
            metric_bundle = metric_bundle.prepend_dimensions(input_selectors)

        return ExecutionResult.build_from_output_bundle(
            definition,
            cmec_output_bundle=output_bundle,
            cmec_metric_bundle=metric_bundle,
        )
