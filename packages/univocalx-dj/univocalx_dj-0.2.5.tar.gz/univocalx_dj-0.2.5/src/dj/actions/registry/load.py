from logging import Logger, getLogger

from sqlalchemy.exc import IntegrityError

from dj.actions.inspect import FileInspector
from dj.actions.registry.base import BaseAction
from dj.actions.registry.models import DatasetRecord, FileRecord
from dj.schemes import FileMetadata, LoadDataConfig
from dj.utils import collect_files, delay, merge_s3uri, pretty_bar

logger: Logger = getLogger(__name__)


class DataLoader(BaseAction):
    def _gather_datafiles(self, data_src: str, filters: list[str] | None) -> set[str]:
        datafiles: set[str] = set()

        logger.info(f"attempting to gather data, filters: {filters}")
        if data_src.startswith("s3://"):
            logger.info("gathering data from S3")
            s3objcets: list[str] = self.storage.list_objects(
                data_src,
                filters,
            )

            for s3obj in s3objcets:
                datafiles.add(merge_s3uri(data_src, s3obj))
        else:
            logger.info("gathering data from local storage")
            datafiles = collect_files(data_src, filters, recursive=True)

        logger.info(f"Gathered {len(datafiles)} file\\s")
        return datafiles

    def _load_datafile(
        self, load_cfg: LoadDataConfig, dataset: DatasetRecord, datafile_src: str
    ) -> FileRecord:
        with self._get_local_file(datafile_src) as local_path:
            # Inspect File Metadata
            metadata: FileMetadata = FileInspector(local_path).metadata

            # Create a data file record
            with self.journalist.transaction():
                datafile_record: FileRecord = self.journalist.add_file_record(
                    dataset=dataset,
                    s3bucket=self.cfg.s3bucket,  # type: ignore[arg-type]
                    s3prefix=self.cfg.s3prefix,
                    filename=metadata.filename,
                    sha256=metadata.sha256,
                    mime_type=metadata.mime_type,
                    size_bytes=metadata.size_bytes,
                    stage=load_cfg.stage,
                    tags=load_cfg.tags,
                )

                self.storage.upload(metadata.filepath, datafile_record.s3uri, False)  # type: ignore[arg-type]
            return datafile_record

    def load(self, load_cfg: LoadDataConfig) -> dict[str, FileRecord]:
        logger.info(f'Starting to load data from "{load_cfg.data_src}"')

        datafiles: set[str] = self._gather_datafiles(
            load_cfg.data_src, load_cfg.filters
        )
        if not datafiles:
            raise ValueError(f"Failed to gather data files from {load_cfg.data_src}")

        # Create\Get a dataset record
        dataset_record: DatasetRecord = self.journalist.add_dataset(
            load_cfg.domain,
            load_cfg.dataset_name,
            load_cfg.description,
            load_cfg.exists_ok,
        )

        # Load files
        logger.info(f"Starting to process {len(datafiles)} file\\s")
        processed_datafiles: dict[str, FileRecord] = {}
        delay()
        for datafile in pretty_bar(
            datafiles, disable=self.cfg.plain, desc="☁️   Loading", unit="file"
        ):
            try:
                datafile_record: FileRecord = self._load_datafile(
                    load_cfg, dataset_record, datafile
                )
                processed_datafiles[datafile] = datafile_record
            except IntegrityError as e:
                if "UNIQUE constraint" in str(e.orig):
                    logger.warning(
                        f'File {datafile} already exists in dataset "{load_cfg.domain}\\{load_cfg.dataset_name}"'
                    )
            except Exception:
                logger.exception(f"Failed to load {datafile}.\n")

        if not processed_datafiles:
            raise ValueError(f"Failed to load datafiles ({load_cfg.data_src}).")

        return processed_datafiles
