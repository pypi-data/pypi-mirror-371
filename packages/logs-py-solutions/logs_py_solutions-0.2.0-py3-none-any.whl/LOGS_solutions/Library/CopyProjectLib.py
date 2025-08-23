import os
import shutil
import tempfile
from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from typing import Any, Callable, Dict, List, Optional, TypeVar, Union, cast, overload
from zipfile import ZipFile

from LOGS import LOGS, Entity
from LOGS.Auxiliary import LOGSException, Tools
from LOGS.Entities import (
    CustomField,
    CustomFieldRequestParameter,
    CustomType,
    CustomTypeRequestParameter,
    Dataset,
    DatasetRequestParameter,
    Document,
    DocumentRequestParameter,
    EntitiesRequestParameter,
    Experiment,
    ExperimentRequestParameter,
    Instrument,
    InstrumentRequestParameter,
    Method,
    MethodRequestParameter,
    Origin,
    Person,
    PersonRequestParameter,
    Project,
    ProjectMinimal,
    ProjectRequestParameter,
    Sample,
    SampleRequestParameter,
)
from LOGS.Interfaces.ITypedEntity import ITypedEntity

ID_TYPE = Union[int, str]
T = TypeVar("T", bound=Entity)


def unique(l):
    return list(set(l))


class MappingMode(Enum):
    Uid = "Uid"
    Name = "Name"
    Custom = "Custom"


@dataclass
class CopyParameters:
    # projectFrom: Optional[datetime] = None
    # sampleFrom: Optional[datetime] = None
    # documentFrom: Optional[datetime] = None
    datasetFrom: Optional[datetime] = None
    # instrumentFrom: Optional[datetime] = None
    # methodFrom: Optional[datetime] = None
    # personFrom: Optional[datetime] = None
    # experimentFrom: Optional[datetime] = None

    projectsMapper: Optional[
        Callable[[Dict[int, Project], LOGS], Dict[int, Project]]
    ] = None
    samplesMapper: Optional[Callable[[Dict[int, Sample], LOGS], Dict[int, Sample]]] = (
        None
    )
    documentsMapper: Optional[
        Callable[[Dict[int, Document], LOGS], Dict[int, Document]]
    ] = None
    datasetsMapper: Optional[
        Callable[[Dict[int, Dataset], LOGS], Dict[int, Dataset]]
    ] = None
    instrumentsMapper: Optional[
        Callable[[Dict[int, Instrument], LOGS], Dict[int, Instrument]]
    ] = None
    methodsMapper: Optional[Callable[[Dict[int, Method], LOGS], Dict[int, Method]]] = (
        None
    )
    personsMapper: Optional[Callable[[Dict[int, Person], LOGS], Dict[int, Person]]] = (
        None
    )
    experimentsMapper: Optional[
        Callable[[Dict[int, Experiment], LOGS], Dict[int, Experiment]]
    ] = None

    customTypesMapper: Optional[
        Callable[[Dict[int, CustomType], LOGS], Dict[int, CustomType]]
    ] = None

    customFieldsMapper: Optional[
        Callable[[Dict[int, CustomField], LOGS], Dict[int, CustomField]]
    ] = None

    projectValidator: Optional[Callable[[Project], bool]] = None
    sampleValidator: Optional[Callable[[Sample], bool]] = None
    documentValidator: Optional[Callable[[Document], bool]] = None
    datasetValidator: Optional[Callable[[Dataset], bool]] = None
    instrumentValidator: Optional[Callable[[Instrument], bool]] = None
    methodValidator: Optional[Callable[[Method], bool]] = None
    personValidator: Optional[Callable[[Person], bool]] = None
    experimentValidator: Optional[Callable[[Experiment], bool]] = None
    customTypeValidator: Optional[Callable[[CustomType], bool]] = None
    customFieldValidator: Optional[Callable[[CustomField], bool]] = None

    projectModifier: Optional[Callable[[Project], Project]] = None
    sampleModifier: Optional[Callable[[Sample], Sample]] = None
    documentModifier: Optional[Callable[[Document], Document]] = None
    datasetModifier: Optional[Callable[[Dataset], Dataset]] = None
    instrumentModifier: Optional[Callable[[Instrument], Instrument]] = None
    methodModifier: Optional[Callable[[Method], Method]] = None
    personModifier: Optional[Callable[[Person], Person]] = None
    experimentModifier: Optional[Callable[[Experiment], Experiment]] = None
    customTypeModifier: Optional[Callable[[CustomType], CustomType]] = None
    customFieldModifier: Optional[Callable[[CustomField], CustomField]] = None

    projectMappingMode: MappingMode = MappingMode.Uid
    sampleMappingMode: MappingMode = MappingMode.Uid
    documentMappingMode: MappingMode = MappingMode.Uid
    datasetMappingMode: MappingMode = MappingMode.Uid
    instrumentMappingMode: MappingMode = MappingMode.Uid
    methodMappingMode: MappingMode = MappingMode.Name
    personMappingMode: MappingMode = MappingMode.Uid
    experimentMappingMode: MappingMode = MappingMode.Name
    customTypeMappingMode: MappingMode = MappingMode.Uid
    customFieldMappingMode: MappingMode = MappingMode.Uid

    originCreateMissing: bool = True
    projectCreateMissing: bool = True
    sampleCreateMissing: bool = True
    documentCreateMissing: bool = False
    datasetCreateMissing: bool = True
    instrumentCreateMissing: bool = True
    methodCreateMissing: bool = True
    personCreateMissing: bool = True
    experimentCreateMissing: bool = True
    customTypeCreateMissing: bool = True
    customFieldCreateMissing: bool = True

    defaultProjectName: Optional[str] = None
    defaultSampleName: Optional[str] = None
    datasetExcludeIds: Optional[List[int]] = None

    projectShowMapping: bool = False
    sampleShowMapping: bool = False
    documentShowMapping: bool = False
    datasetShowMapping: bool = False
    instrumentShowMapping: bool = False
    methodShowMapping: bool = False
    personShowMapping: bool = False
    experimentShowMapping: bool = False
    customTypeShowMapping: bool = False
    customFieldShowMapping: bool = False


class EntityCollection:
    """Helper class for CopyProject. Contains a collection of all LOGS entities types."""

    def __init__(self) -> None:
        self.origins: Dict[int, Origin] = {}
        self.projects: Dict[int, Project] = {}
        self.samples: Dict[int, Sample] = {}
        self.documents: Dict[int, Document] = {}
        self.datasets: Dict[int, Dataset] = {}
        self.instruments: Dict[int, Instrument] = {}
        self.methods: Dict[int, Method] = {}
        self.persons: Dict[int, Person] = {}
        self.experiments: Dict[int, Experiment] = {}
        self.customTypes: Dict[int, CustomType] = {}
        self.customFields: Dict[int, CustomField] = {}

    def getNewestDatasetDate(self):
        if not self.datasets:
            return None
        return max(d.dateAdded for d in self.datasets.values() if d.dateAdded)

    def __len__(self):
        return (
            len(self.origins.keys())
            + len(self.projects.keys())
            + len(self.samples.keys())
            + len(self.documents.keys())
            + len(self.datasets.keys())
            + len(self.instruments.keys())
            + len(self.methods.keys())
            + len(self.persons.keys())
            + len(self.experiments.keys())
            + len(self.customTypes.keys())
            + len(self.customFields.keys())
        )

    def printSummary(self, prefix="Found", postfix="to copy."):
        """Print the counts of each LOGS entity type."""

        print(
            f"{prefix} {Tools.numberPlural('project', len(self.projects.keys()))} {postfix}"
        )
        print(
            f"{prefix} {Tools.numberPlural('sample', len(self.samples.keys()))} {postfix}"
        )
        print(
            f"{prefix} {Tools.numberPlural('document', len(self.documents.keys()))} {postfix}"
        )
        print(
            f"{prefix} {Tools.numberPlural('dataset', len(self.datasets.keys()))} {postfix}"
        )
        print(
            f"{prefix} {Tools.numberPlural('instrument', len(self.instruments.keys()))} {postfix}"
        )
        print(
            f"{prefix} {Tools.numberPlural('method', len(self.methods.keys()))} {postfix}"
        )
        print(
            f"{prefix} {Tools.numberPlural('person', len(self.persons.keys()))} {postfix}"
        )
        print(
            f"{prefix} {Tools.numberPlural('experiment', len(self.experiments.keys()))} {postfix}"
        )
        print(
            f"{prefix} {Tools.numberPlural('customType', len(self.customTypes.keys()))} {postfix}"
        )
        print(
            f"{prefix} {Tools.numberPlural('customField', len(self.customFields.keys()))} {postfix}"
        )


class CopyProject:
    """Copies a project from a source LOGS to of a target LOGS."""

    def __init__(
        self,
        sourceLogs: LOGS,
        targetLogs: LOGS,
        parameters: Optional[CopyParameters] = None,
    ):
        """Constructor of CopyProject

        Args:
            sourceLogs: The LOGS object connected to gather project data from
            targetLogs: The LOGS object connected to the copy the project contents to
        """
        self.sourceLogs = sourceLogs
        self.targetLogs = targetLogs
        self.parameters = parameters if parameters else CopyParameters()

        self.collection = EntityCollection()
        self.mapping = EntityCollection()

        self.unknownCount = 0
        self.forceDefaultSample = False

    def collectEntitiesFromProject(
        self, projectName: str, collection: Optional[EntityCollection] = None
    ):
        """Collects entities based on specified projects

        Args:
            projectNames: Name list for project selection to collect entities from. Defaults to [].
            projectTags: Tag list for project selection to collect entities from. Defaults to [].

        Raises:
            Exception: Throws if source projects are not

        Returns:
            A collection of entities from the source projects.
        """

        project = self.sourceLogs.projects(
            ProjectRequestParameter(names=[projectName])
        ).first()

        if not project:
            raise Exception(f"Source project '{projectName}' not found")

        samples: Dict[int, Sample] = {}
        # Samples from source
        if self.parameters.sampleCreateMissing:
            request3 = self.sourceLogs.samples(
                SampleRequestParameter(projectIds=[project.id])
            )
            print("+++ Collecting %d samples from source +++" % request3.count)
            samples = {sample.id: sample for sample in request3}

        # Documents from source
        documents: Dict[int, Document] = {}
        if self.parameters.documentCreateMissing:
            request4 = self.sourceLogs.documents(
                DocumentRequestParameter(projectIds=[project.id])
            )
            print("+++ Collecting %d documents from source +++" % request4.count)
            documents = {dataset.id: dataset for dataset in request4}

        # Datasets from source
        datasets: Dict[int, Dataset] = {}
        if self.parameters.datasetCreateMissing:
            request5 = self.sourceLogs.datasets(
                DatasetRequestParameter(
                    projectIds=[project.id],
                    createdFrom=self.parameters.datasetFrom,
                    excludeIds=self.parameters.datasetExcludeIds,
                )
            )
            print("+++ Collecting %d datasets from source +++" % request5.count)
            datasets = {dataset.id: dataset for dataset in request5}

        print("+++ Collecting related entities +++")
        sampleIds = [
            dataset.sample.id for dataset in datasets.values() if dataset.sample
        ]
        samples.update(
            {
                sample.id: sample
                for sample in self.sourceLogs.samples(
                    SampleRequestParameter(ids=sampleIds)
                )
            }
        )

        # Instruments from source
        instrumentIds = [
            dataset.instrumentId
            for dataset in datasets.values()
            if dataset.instrumentId
        ]
        instrumentIds = unique(instrumentIds)
        instruments = {
            instrument.id: instrument
            for instrument in self.sourceLogs.instruments(
                InstrumentRequestParameter(ids=instrumentIds)
            )
        }

        # Experiments from source
        experimentIds = [
            dataset.experiment.id for dataset in datasets.values() if dataset.experiment
        ]
        experimentIds = unique(experimentIds)
        experiments = {
            experiment.id: experiment
            for experiment in self.sourceLogs.experiments(
                ExperimentRequestParameter(ids=experimentIds)
            )
        }

        # Methods from source
        methodIds = [
            dataset.methodId for dataset in datasets.values() if dataset.methodId
        ]

        methodIds.extend(
            instrument.methodId
            for instrument in instruments.values()
            if instrument.methodId
        )
        methodIds.extend(
            experiment.method.id
            for experiment in experiments.values()
            if experiment.method
        )

        methodIds = unique(methodIds)

        methods = {
            method.id: method
            for method in self.sourceLogs.methods(MethodRequestParameter(ids=methodIds))
        }

        # Persons from other entities
        personIds = list(sample.owner.id for sample in samples.values() if sample.owner)
        personIds.extend(
            person.id
            for sample in samples.values()
            if sample.preparedBy
            for person in sample.preparedBy
        )

        personIds.extend(
            dataset.owner.id for dataset in datasets.values() if dataset.owner
        )
        personIds.extend(
            id
            for dataset in datasets.values()
            if dataset.operatorIds
            for id in dataset.operatorIds
        )

        personIds = unique(personIds)

        persons = {
            person.id: person
            for person in self.sourceLogs.persons(PersonRequestParameter(ids=personIds))
        }

        # Collecting entity types
        customTypeIds = set(
            sample.customType.id for sample in samples.values() if sample.customType
        ).union(
            set(
                dataset.customType.id
                for dataset in datasets.values()
                if dataset.customType
            )
        )
        customTypeIds = list(customTypeIds)

        customTypes = {
            customType.id: customType
            for customType in self.sourceLogs.customTypes(
                CustomTypeRequestParameter(ids=customTypeIds)
            )
        }

        # Collecting custom fields
        customFieldIds = list(
            set(
                [
                    field.id
                    for customType in customTypes.values()
                    for field in customType.customFields
                ]
            )
        )

        customFields = {
            customField.id: customField
            for customField in self.sourceLogs.customFields(
                CustomFieldRequestParameter(ids=customFieldIds)
            )
        }

        if collection is None:
            collection = EntityCollection()
        # collection.origins.update({origin.id: origin})
        collection.projects.update({project.id: project})
        collection.samples.update(samples.items())
        collection.documents.update(documents.items())
        collection.datasets.update(datasets.items())
        collection.instruments.update(instruments.items())
        collection.methods.update(methods.items())
        collection.persons.update(persons.items())
        collection.experiments.update(experiments.items())
        collection.customTypes.update(customTypes.items())
        collection.customFields.update(customFields.items())

        return collection

    @overload
    def _uidMapper(self, entities: Dict[int, T], logs: LOGS) -> Dict[int, T]: ...

    @overload
    def _uidMapper(self, entities: Dict[str, T], logs: LOGS) -> Dict[str, T]: ...

    def _uidMapper(self, entities: Dict[Any, T], logs: LOGS) -> Dict[Any, T]:
        result: Dict[ID_TYPE, T] = {}
        mapper = {
            str(cast(Any, v).uid): k
            for k, v in entities.items()
            if hasattr(v, "uid") and getattr(v, "uid")
        }

        for targetEntity in logs.entities(
            EntitiesRequestParameter(uids=list(mapper.keys()))
        ):
            knownEntity = entities[mapper[str(targetEntity.uid)]]
            result[knownEntity.id] = targetEntity

        return result

    @overload
    def _nameMapper(self, entities: Dict[int, T], logs: LOGS) -> Dict[int, T]: ...

    @overload
    def _nameMapper(self, entities: Dict[str, T], logs: LOGS) -> Dict[str, T]: ...

    def _nameMapper(self, entities: Dict[Any, T], logs: LOGS) -> Dict[Any, T]:
        result: Dict[ID_TYPE, T] = {}
        mapper = {
            getattr(v, "name"): k for k, v in entities.items() if hasattr(v, "name")
        }

        for targetEntity in logs.entities(
            EntitiesRequestParameter(names=list(mapper.keys()))
        ):
            if not targetEntity.name or targetEntity.name not in mapper:
                continue
            knownEntity = entities[mapper[targetEntity.name]]

            # ignore if entity type is not equal
            if (
                type(targetEntity).__name__.replace("Minimal", "")
                != type(knownEntity).__name__
            ):
                continue

            result[knownEntity.id] = targetEntity

        return result

    def _duplicatedCustomFieldNameCheck(
        self, customFields: Dict[int, CustomField], logs: LOGS
    ):
        postFix = " (imported)"

        while True:
            lookUp = {
                customField.name: customField for customField in customFields.values()
            }

            found = False
            for customField in logs.customFields(CustomFieldRequestParameter()):
                if customField.name not in lookUp:
                    continue
                if lookUp[customField.name].name is None:
                    lookUp[customField.name].name = ""
                lookUp[customField.name].name += cast(Any, postFix)

                found = True

            if not found:
                break

        return customFields

    def _duplicatedCustomTypeNameCheck(
        self, customTypes: Dict[int, CustomType], logs: LOGS
    ):
        postFix = " (imported)"

        while True:
            lookUp = {
                customType.name: customType for customType in customTypes.values()
            }

            found = False
            for customType in logs.customTypes(CustomTypeRequestParameter()):
                if customType.name not in lookUp:
                    continue
                if lookUp[customType.name].name is None:
                    lookUp[customType.name].name = ""
                lookUp[customType.name].name += cast(Any, postFix)
                found = True

            if not found:
                break

        return customTypes

    def _uniqueNameEntities(self):
        self.collection.customFields = self._duplicatedCustomFieldNameCheck(
            self.collection.customFields, self.targetLogs
        )

        self.collection.customTypes = self._duplicatedCustomTypeNameCheck(
            self.collection.customTypes, self.targetLogs
        )

    def _createUidMapping(self):
        self.mapping.origins.update(
            self._uidMapper(self.collection.origins, self.targetLogs)
        )
        self.mapping.projects.update(
            self._uidMapper(self.collection.projects, self.targetLogs)
        )
        self.mapping.samples.update(
            self._uidMapper(self.collection.samples, self.targetLogs)
        )
        self.mapping.documents.update(
            self._uidMapper(self.collection.documents, self.targetLogs)
        )
        self.mapping.datasets.update(
            self._uidMapper(self.collection.datasets, self.targetLogs)
        )
        self.mapping.instruments.update(
            self._uidMapper(self.collection.instruments, self.targetLogs)
        )
        self.mapping.methods.update(
            self._uidMapper(self.collection.methods, self.targetLogs)
        )
        self.mapping.persons.update(
            self._uidMapper(self.collection.persons, self.targetLogs)
        )
        self.mapping.experiments.update(
            self._uidMapper(self.collection.experiments, self.targetLogs)
        )
        self.mapping.customTypes.update(
            self._uidMapper(self.collection.customTypes, self.targetLogs)
        )
        self.mapping.customFields.update(
            self._uidMapper(self.collection.customFields, self.targetLogs)
        )

    def _createMapping(self):
        if self.parameters.projectMappingMode == MappingMode.Name:
            self.mapping.projects.update(
                self._nameMapper(self.collection.projects, self.targetLogs)
            )
        elif (
            self.parameters.projectMappingMode == MappingMode.Custom
            and self.parameters.projectsMapper
        ):
            self.mapping.projects.update(
                self.parameters.projectsMapper(
                    self.collection.projects, self.targetLogs
                )
            )

        if self.parameters.sampleMappingMode == MappingMode.Name:
            self.mapping.samples.update(
                self._nameMapper(self.collection.samples, self.targetLogs)
            )
        elif (
            self.parameters.sampleMappingMode == MappingMode.Custom
            and self.parameters.samplesMapper
        ):
            self.mapping.samples.update(
                self.parameters.samplesMapper(self.collection.samples, self.targetLogs)
            )

        if self.parameters.documentMappingMode == MappingMode.Name:
            self.mapping.documents.update(
                self._nameMapper(self.collection.documents, self.targetLogs)
            )
        elif (
            self.parameters.documentMappingMode == MappingMode.Custom
            and self.parameters.documentsMapper
        ):
            self.mapping.documents.update(
                self.parameters.documentsMapper(
                    self.collection.documents, self.targetLogs
                )
            )

        if self.parameters.datasetMappingMode == MappingMode.Name:
            self.mapping.datasets.update(
                self._nameMapper(self.collection.datasets, self.targetLogs)
            )
        elif (
            self.parameters.datasetMappingMode == MappingMode.Custom
            and self.parameters.datasetsMapper
        ):
            self.mapping.datasets.update(
                self.parameters.datasetsMapper(
                    self.collection.datasets, self.targetLogs
                )
            )

        if self.parameters.instrumentMappingMode == MappingMode.Name:
            self.mapping.instruments.update(
                self._nameMapper(self.collection.instruments, self.targetLogs)
            )
        elif (
            self.parameters.instrumentMappingMode == MappingMode.Custom
            and self.parameters.instrumentsMapper
        ):
            self.mapping.instruments.update(
                self.parameters.instrumentsMapper(
                    self.collection.instruments, self.targetLogs
                )
            )

        if self.parameters.methodMappingMode == MappingMode.Name:
            self.mapping.methods.update(
                self._nameMapper(self.collection.methods, self.targetLogs)
            )
        elif (
            self.parameters.methodMappingMode == MappingMode.Custom
            and self.parameters.methodsMapper
        ):
            self.mapping.methods.update(
                self.parameters.methodsMapper(self.collection.methods, self.targetLogs)
            )

        if self.parameters.personMappingMode == MappingMode.Name:
            self.mapping.persons.update(
                self._nameMapper(self.collection.persons, self.targetLogs)
            )
        elif (
            self.parameters.personMappingMode == MappingMode.Custom
            and self.parameters.personsMapper
        ):
            self.mapping.persons.update(
                self.parameters.personsMapper(self.collection.persons, self.targetLogs)
            )

        if self.parameters.experimentMappingMode == MappingMode.Name:
            self.mapping.experiments.update(
                self._nameMapper(self.collection.experiments, self.targetLogs)
            )
        elif (
            self.parameters.experimentMappingMode == MappingMode.Custom
            and self.parameters.experimentsMapper
        ):
            self.mapping.experiments.update(
                self.parameters.experimentsMapper(
                    self.collection.experiments, self.targetLogs
                )
            )

        if self.parameters.customTypeMappingMode == MappingMode.Name:
            self.mapping.customTypes.update(
                self._nameMapper(self.collection.customTypes, self.targetLogs)
            )
        elif (
            self.parameters.customTypeMappingMode == MappingMode.Custom
            and self.parameters.customTypesMapper
        ):
            self.mapping.customTypes.update(
                self.parameters.customTypesMapper(
                    self.collection.customTypes, self.targetLogs
                )
            )

        if self.parameters.customFieldMappingMode == MappingMode.Name:
            self.mapping.customFields.update(
                self._nameMapper(self.collection.customFields, self.targetLogs)
            )
        elif (
            self.parameters.customFieldMappingMode == MappingMode.Custom
            and self.parameters.customFieldsMapper
        ):
            self.mapping.customFields.update(
                self.parameters.customFieldsMapper(
                    self.collection.customFields, self.targetLogs
                )
            )

    def _modifyEntities(self):
        if self.parameters.projectModifier:
            self.collection.projects = {
                k: self.parameters.projectModifier(v)
                for k, v in self.collection.projects.items()
            }
        if self.parameters.sampleModifier:
            self.collection.samples = {
                k: self.parameters.sampleModifier(v)
                for k, v in self.collection.samples.items()
            }
        if self.parameters.documentModifier:
            self.collection.documents = {
                k: self.parameters.documentModifier(v)
                for k, v in self.collection.documents.items()
            }
        if self.parameters.datasetModifier:
            self.collection.datasets = {
                k: self.parameters.datasetModifier(v)
                for k, v in self.collection.datasets.items()
            }
        if self.parameters.instrumentModifier:
            self.collection.instruments = {
                k: self.parameters.instrumentModifier(v)
                for k, v in self.collection.instruments.items()
            }
        if self.parameters.methodModifier:
            self.collection.methods = {
                k: self.parameters.methodModifier(v)
                for k, v in self.collection.methods.items()
            }
        if self.parameters.personModifier:
            self.collection.persons = {
                k: self.parameters.personModifier(v)
                for k, v in self.collection.persons.items()
            }
        if self.parameters.experimentModifier:
            self.collection.experiments = {
                k: self.parameters.experimentModifier(v)
                for k, v in self.collection.experiments.items()
            }

    @overload
    def _filterUnknownByMap(
        self,
        entities: Dict[int, T],
        known: Dict[int, T],
    ): ...

    @overload
    def _filterUnknownByMap(
        self,
        entities: Dict[str, T],
        known: Dict[str, T],
    ): ...

    def _filterUnknownByMap(
        self,
        entities: Dict[Any, T],
        known: Dict[Any, T],
    ):
        keys = list(entities.keys())

        for k in keys:
            if k in known and known[k] is not None:
                print(
                    "%s with name %a already exists and will be skipped."
                    % (
                        type(known[k]).__name__.replace("Minimal", ""),
                        getattr(known[k], "name") if hasattr(known[k], "name") else "",
                    )
                )
                del entities[k]

    @overload
    def _showMappingForEntity(self, entities: Dict[int, T], mapping: Dict[int, T]): ...

    @overload
    def _showMappingForEntity(self, entities: Dict[str, T], mapping: Dict[str, T]): ...

    def _showMappingForEntity(self, entities: Dict[Any, T], mapping: Dict[Any, T]):
        for id, entity in entities.items():
            print(
                f"{entity} => {mapping[id] if id in mapping and mapping[id] else 'None'}"
            )

    def _showMapping(self):
        if self.parameters.projectShowMapping:
            self._showMappingForEntity(self.collection.projects, self.mapping.projects)

        if self.parameters.sampleShowMapping:
            self._showMappingForEntity(self.collection.samples, self.mapping.samples)

        if self.parameters.documentShowMapping:
            self._showMappingForEntity(
                self.collection.documents, self.mapping.documents
            )

        if self.parameters.datasetShowMapping:
            self._showMappingForEntity(self.collection.datasets, self.mapping.datasets)

        if self.parameters.instrumentShowMapping:
            self._showMappingForEntity(
                self.collection.instruments, self.mapping.instruments
            )

        if self.parameters.methodShowMapping:
            self._showMappingForEntity(self.collection.methods, self.mapping.methods)

        if self.parameters.personShowMapping:
            self._showMappingForEntity(self.collection.persons, self.mapping.persons)

        if self.parameters.experimentShowMapping:
            self._showMappingForEntity(
                self.collection.experiments, self.mapping.experiments
            )

        if self.parameters.customTypeShowMapping:
            self._showMappingForEntity(
                self.collection.customTypes, self.mapping.customTypes
            )

        if self.parameters.customFieldShowMapping:
            self._showMappingForEntity(
                self.collection.customFields, self.mapping.customFields
            )

    def _filterKnown(self):
        self._createUidMapping()
        self._modifyEntities()
        self._createMapping()
        self._uniqueNameEntities()

        if self.parameters.experimentShowMapping:
            self._showMappingForEntity(
                self.collection.experiments, self.mapping.experiments
            )

        self._showMapping()

        if self.parameters.originCreateMissing:
            self._filterUnknownByMap(self.collection.origins, self.mapping.origins)
        else:
            self.collection.origins = {}

        if self.parameters.projectCreateMissing:
            self._filterUnknownByMap(self.collection.projects, self.mapping.projects)
        else:
            self.collection.projects = {}

        if self.parameters.sampleCreateMissing:
            self._filterUnknownByMap(self.collection.samples, self.mapping.samples)
        else:
            self.collection.samples = {}

        if self.parameters.documentCreateMissing:
            self._filterUnknownByMap(self.collection.documents, self.mapping.documents)
        else:
            self.collection.documents = {}

        if self.parameters.datasetCreateMissing:
            self._filterUnknownByMap(self.collection.datasets, self.mapping.datasets)
        else:
            self.collection.datasets = {}

        if self.parameters.instrumentCreateMissing:
            self._filterUnknownByMap(
                self.collection.instruments, self.mapping.instruments
            )
        else:
            self.collection.instruments = {}

        if self.parameters.methodCreateMissing:
            self._filterUnknownByMap(self.collection.methods, self.mapping.methods)
        else:
            self.collection.methods = {}

        if self.parameters.personCreateMissing:
            self._filterUnknownByMap(self.collection.persons, self.mapping.persons)
        else:
            self.collection.persons = {}

        if self.parameters.experimentCreateMissing:
            self._filterUnknownByMap(
                self.collection.experiments, self.mapping.experiments
            )
        else:
            self.collection.experiments = {}

        if self.parameters.customTypeCreateMissing:
            self._filterUnknownByMap(
                self.collection.customTypes, self.mapping.customTypes
            )
        else:
            self.collection.customTypes = {}

        if self.parameters.customFieldCreateMissing:
            self._filterUnknownByMap(
                self.collection.customFields, self.mapping.customFields
            )
        else:
            self.collection.customFields = {}

    @classmethod
    def _mapEntities(cls, orig, mapping):
        if orig == None:
            return None

        single = True
        if isinstance(orig, list):
            single = False
        else:
            orig = [orig]

        mapped = [mapping[o.id] for o in orig if o.id in mapping]

        if single:
            if mapped:
                return mapped[0]
            else:
                return None
        return mapped

    @classmethod
    def _mapOwner(cls, entities: List[Entity], mapping: Dict[int, Person]):
        for e in entities:
            if hasattr(e, "owner"):
                setattr(e, "owner", cls._mapEntities(getattr(e, "owner"), mapping))

    @classmethod
    def _mapCustomFields(cls, entities: List[Entity], mapping: Dict[int, CustomField]):
        for e in entities:
            if isinstance(e, ITypedEntity):
                values = []

                if e.customFieldValues:
                    for v in e.customFieldValues:
                        if v.id in mapping:
                            v.id = mapping[v.id].id
                            values.append(v)

                e.customValues = values

    def _createEntities(self):
        temporaryDirectory = tempfile.TemporaryDirectory()
        tempdir = temporaryDirectory.name

        statistics = EntityCollection()

        if not os.path.exists(tempdir):
            raise Exception("Temp path %a does not exist" % tempdir)

        if not os.path.isdir(tempdir):
            raise Exception("Temp path %a is not a directory" % tempdir)

        ## Create default origin
        origin = cast(
            Origin | None,
            self.targetLogs.entities(
                EntitiesRequestParameter(uids=[str(self.sourceLogs.uid)])
            ).first(),
        )

        number = 0
        if not origin and self.parameters.originCreateMissing:
            origin = self.sourceLogs.instanceOrigin
            self.targetLogs.create(origin)

        ## Create origins
        number += len(self.collection.origins.keys())
        count = 0
        for id, origin in self.collection.origins.items():
            count += 1
            p = 100.0 * count / number
            print("%.1f%% Creating" % p, origin, origin.url)
            self.targetLogs.create(origin)
            self.mapping.origins[id] = origin
            statistics.origins[id] = origin

        ## Set default target project
        if self.parameters.defaultProjectName:
            defaultProject = self.targetLogs.projects(
                ProjectRequestParameter(names=[self.parameters.defaultProjectName])
            ).first()

            if not defaultProject:
                raise Exception(
                    f"Target project '{self.parameters.defaultProjectName}' not found"
                )
        else:
            defaultProject = (
                list(self.collection.projects.values())[0]
                if self.collection.projects
                else None
            )

        ## Set default target sample
        if self.parameters.defaultSampleName:
            defaultSample = self.targetLogs.samples(
                SampleRequestParameter(names=[self.parameters.defaultSampleName])
            ).first()

            if not defaultSample:
                raise Exception(
                    f"Target Sample '{self.parameters.defaultSampleName}' not found"
                )
            self.forceDefaultSample = True
        else:
            defaultSample = (
                list(self.collection.samples.values())[0]
                if self.collection.samples
                else None
            )

        ## Create custom fields
        number += len(self.collection.customFields.keys())
        count = 0
        for id, customField in self.collection.customFields.items():
            count += 1
            p = 100.0 * count / number
            print("%.1f%% Creating" % p, customField)

            if (
                self.parameters.customFieldValidator
                and not self.parameters.customFieldValidator(customField)
            ):
                continue

            customField.setOrigin(uid=customField.uid, origin=origin)
            self.mapping.customFields[id] = customField
            statistics.customFields[id] = customField
            self.targetLogs.create(customField)

        ## Create custom types
        number += len(self.collection.customTypes.keys())
        count = 0
        for id, customType in self.collection.customTypes.items():
            count += 1
            p = 100.0 * count / number
            print("%.1f%% Creating" % p, customType)

            if not customType.sections:
                customType.sections = []

            for sections in customType.sections:
                if sections.customFields:
                    fields = []
                    for field in sections.customFields:
                        field = self._mapEntities(field, self.mapping.customFields)
                        if field:
                            fields.append(field)
                    sections.customFields = [CustomField(id=f.id) for f in fields]

            if (
                self.parameters.customTypeValidator
                and not self.parameters.customTypeValidator(customType)
            ):
                continue

            customType.setOrigin(uid=customType.uid, origin=origin)
            self.mapping.customTypes[id] = customType
            statistics.customTypes[id] = customType
            self.targetLogs.create(customType)

        ## Create persons
        number = len(self.collection.persons.keys())
        count = 0
        for id, person in self.collection.persons.items():
            if self.parameters and self.parameters.personModifier:
                person = self.parameters.personModifier(person)
            # person.roles = None

            if not person.salutation:
                person.salutation = "Mrs."
            count += 1
            p = 100.0 * count / number

            print("%.1f%% Creating" % p, person)

            if self.parameters.personValidator and not self.parameters.personValidator(
                person
            ):
                continue

            person.setOrigin(uid=person.uid, origin=origin)
            self.mapping.persons[id] = person
            statistics.persons[id] = person
            self.targetLogs.create(person)

        # for k,v in self.mapping.persons.items():
        #     print(k, "->", v.id)

        ## map all owner to target persons
        self._mapOwner(list(self.collection.projects.values()), self.mapping.persons)
        self._mapOwner(list(self.collection.samples.values()), self.mapping.persons)
        self._mapOwner(list(self.collection.documents.values()), self.mapping.persons)
        self._mapOwner(list(self.collection.datasets.values()), self.mapping.persons)
        self._mapOwner(list(self.collection.instruments.values()), self.mapping.persons)
        self._mapOwner(list(self.collection.methods.values()), self.mapping.persons)
        self._mapOwner(list(self.collection.persons.values()), self.mapping.persons)
        self._mapOwner(list(self.collection.experiments.values()), self.mapping.persons)

        ## map all custom fields to target custom fields
        self._mapCustomFields(
            list(self.collection.projects.values()), self.mapping.customFields
        )
        self._mapCustomFields(
            list(self.collection.samples.values()), self.mapping.customFields
        )
        self._mapCustomFields(
            list(self.collection.documents.values()), self.mapping.customFields
        )
        self._mapCustomFields(
            list(self.collection.datasets.values()), self.mapping.customFields
        )
        self._mapCustomFields(
            list(self.collection.instruments.values()), self.mapping.customFields
        )
        self._mapCustomFields(
            list(self.collection.methods.values()), self.mapping.customFields
        )
        self._mapCustomFields(
            list(self.collection.persons.values()), self.mapping.customFields
        )
        self._mapCustomFields(
            list(self.collection.experiments.values()), self.mapping.customFields
        )

        ## Create projects
        number = len(self.collection.projects.keys())
        count = 0
        for id, project in self.collection.projects.items():
            count += 1
            p = 100.0 * count / number
            print("%.1f%% Creating" % p, project)
            if project.projectPersonPermissions:
                projectPersonPermissions = []
                for perm in project.projectPersonPermissions:
                    if perm.person:
                        perm.person = self._mapEntities(
                            perm.person, self.collection.persons
                        )
                        if perm.person:
                            projectPersonPermissions.append(perm)
                project.projectPersonPermissions = projectPersonPermissions

            if (
                self.parameters.projectValidator
                and not self.parameters.projectValidator(project)
            ):
                continue

            project.setOrigin(uid=project.uid, origin=origin)
            self.mapping.projects[id] = project
            statistics.projects[id] = project
            self.targetLogs.create(project)

        ## Create methods
        number = len(self.collection.methods.keys())
        count = 0
        for id, method in self.collection.methods.items():
            count += 1
            p = 100.0 * count / number
            print("%.1f%% Creating" % p, method)

            if self.parameters.methodValidator and not self.parameters.methodValidator(
                method
            ):
                continue

            method.setOrigin(uid=method.uid, origin=origin)
            self.mapping.methods[id] = method
            self.targetLogs.create(method)

        ## Create instruments
        number = len(self.collection.instruments.keys())
        count = 0
        for id, instrument in self.collection.instruments.items():
            count += 1
            p = 100.0 * count / number
            print("%.1f%% Creating" % p, instrument)
            instrument.method = self._mapEntities(
                instrument.method, self.mapping.methods
            )

            if (
                self.parameters.instrumentValidator
                and not self.parameters.instrumentValidator(instrument)
            ):
                continue

            instrument.setOrigin(uid=instrument.uid, origin=origin)
            self.mapping.instruments[id] = instrument
            statistics.instruments[id] = instrument
            self.targetLogs.create(instrument)

        ## Create experiments
        number = len(self.collection.experiments.keys())
        count = 0
        for id, experiment in self.collection.experiments.items():
            count += 1
            p = 100.0 * count / number
            print("%.1f%% Creating" % p, experiment)
            experiment.method = self._mapEntities(
                experiment.method, self.mapping.methods
            )
            if not experiment.name:
                self.unknownCount += 1
                experiment.name = "Unknown %d" % self.unknownCount

            if (
                self.parameters.experimentValidator
                and not self.parameters.experimentValidator(experiment)
            ):
                continue

            experiment.setOrigin(uid=experiment.uid, origin=origin)
            self.mapping.experiments[id] = experiment
            statistics.experiments[id] = experiment
            self.targetLogs.create(experiment)

        ## Create samples
        number = len(self.collection.samples.keys())
        count = 0
        for id, sample in self.collection.samples.items():
            count += 1
            p = 100.0 * count / number
            print("%.1f%% Creating" % p, sample)
            sample.preparedBy = self._mapEntities(
                sample.preparedBy, self.mapping.persons
            )

            if not sample.projects:
                sample.projects = []

            sample.projects = self._mapEntities(sample.projects, self.mapping.projects)
            if defaultProject:
                if not sample.projects:
                    sample.projects = [defaultProject]
                else:
                    sample.projects.append(defaultProject)

            sample.customType = self._mapEntities(
                sample.customType, self.mapping.customTypes
            )

            if self.parameters.sampleValidator and not self.parameters.sampleValidator(
                sample
            ):
                continue

            sample.setOrigin(uid=sample.uid, origin=origin)
            self.mapping.samples[id] = sample
            statistics.samples[id] = sample
            self.targetLogs.create(sample)

        ## Create datasets
        number = len(self.collection.datasets.keys())
        count = 0
        for id, dataset in self.collection.datasets.items():
            count += 1
            p = 100.0 * count / number
            print("%.1f%% Creating" % p, dataset)
            zipName = "dataset_%s" % id
            zipFileName = zipName + ".zip"
            zipDir = os.path.join(tempdir, zipName)
            zipFile = os.path.join(tempdir, zipFileName)
            if os.path.exists(zipFile):
                os.remove(zipFile)

            dataset.download(directory=tempdir, fileName=zipFileName, overwrite=True)
            if not os.path.exists(zipDir):
                with ZipFile(zipFile, "r") as zObject:
                    os.mkdir(zipDir)
                    zObject.extractall(path=zipDir)

            uid = dataset.uid
            dataset = Dataset(dataset, files=zipDir)

            dataset.instrument = self._mapEntities(
                dataset.instrument, self.mapping.instruments
            )
            dataset.method = self._mapEntities(dataset.method, self.mapping.methods)
            dataset.operators = self._mapEntities(
                dataset.operators, self.mapping.persons
            )

            if not dataset.projects:
                dataset.projects = []

            dataset.projects = self._mapEntities(
                dataset.projects, self.mapping.projects
            )

            if defaultProject:
                if not dataset.projects:
                    dataset.projects = [cast(ProjectMinimal, defaultProject)]
                else:
                    dataset.projects.append(cast(ProjectMinimal, defaultProject))

            dataset.sample = self._mapEntities(dataset.sample, self.mapping.samples)
            if defaultSample:
                if self.forceDefaultSample or not dataset.sample:
                    dataset.sample = defaultSample

            dataset.experiment = self._mapEntities(
                dataset.experiment, self.mapping.experiments
            )
            if not (dataset.projects and dataset.sample and dataset.operators):
                dataset.claimed = False
            else:
                dataset.owner = dataset.operators[0]

            if (
                self.parameters.datasetValidator
                and not self.parameters.datasetValidator(dataset)
            ):
                continue

            dataset.setOrigin(uid=uid, origin=origin)

            dataset.customType = self._mapEntities(
                dataset.customType, self.mapping.customTypes
            )

            try:
                self.mapping.datasets[id] = dataset
                statistics.datasets[id] = dataset
                self.targetLogs.create(dataset)

            except LOGSException as e:
                print(
                    " Dataset %a upload failed: '" % dataset.toString() + str(e) + "'"
                )

            os.remove(zipFile)
            shutil.rmtree(zipDir)

        temporaryDirectory.cleanup()
        return statistics

    def getNewestDatasetDate(self):
        return self.collection.getNewestDatasetDate()

    def getMappedDatasetIds(self):
        return list(self.mapping.datasets.keys())

    def copyProjectContent(self, sourceProject):
        self.collection = self.collectEntitiesFromProject(sourceProject)

        self.collection.printSummary(postfix="to copy from source.")
        print()

        self._filterKnown()

        print()
        print(
            "+++ Final number of entities to copy (after removing duplicates and known). +++"
        )
        self.collection.printSummary(postfix="to create on target.")
        print()

        statistics = self._createEntities()

        print()
        print("+++ Created %d entities on target +++" % len(statistics))
        statistics.printSummary(prefix="Created", postfix="on target.")
        print()
        print("+++ >>> Copy finished <<< +++")


if __name__ == "__main__":
    source_key = "XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX"
    source_url = "https://source.logs.com/sorceGroup"

    target_key = "YYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYY"
    target_url = "https://target.logs.com/targetGroup"

    # create two logs instances (source and target LOGS)
    copy = CopyProject(
        LOGS(source_url, source_key),
        LOGS(target_url, target_key),
        CopyParameters(projectCreateMissing=False),
    )

    copy.copyProjectContent("MySourceProjectName")
