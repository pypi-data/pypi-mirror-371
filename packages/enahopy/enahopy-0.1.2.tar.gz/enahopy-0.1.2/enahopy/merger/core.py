"""
ENAHO Merger - Clases Principales (VERSIÓN CORREGIDA)
======================================================

Implementación de las clases principales ENAHOGeoMerger con
funcionalidades completas de fusión geográfica y merge de módulos.

Versión: 2.1.0
Correcciones aplicadas:
- Validación de DataFrames vacíos
- Manejo robusto de CacheManager
- Validación de tipos de datos
- Manejo de NaN en claves de merge
- División por cero en métricas
- Documentación mejorada
"""
"""
Imports centralizados para evitar errores de dependencias.
"""

# Imports estándar de Python (siempre disponibles)
import os
import sys
import time
import logging
import warnings
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Any, Union
from collections import defaultdict, Counter

# Imports científicos (verificar disponibilidad)
try:
    import pandas as pd
    import numpy as np

    HAS_PANDAS = True
except ImportError:
    HAS_PANDAS = False

try:
    import matplotlib.pyplot as plt
    import seaborn as sns

    HAS_PLOTTING = True
except ImportError:
    HAS_PLOTTING = False


# Verificación de dependencias
def check_dependencies():
    """Verifica que todas las dependencias estén disponibles."""
    missing = []

    if not HAS_PANDAS:
        missing.append("pandas")
    if not HAS_PLOTTING:
        missing.append("matplotlib, seaborn")

    if missing:
        raise ImportError(f"Dependencias faltantes: {', '.join(missing)}")

    return True


# Importaciones internas
from .config import (
    GeoMergeConfiguration,
    GeoValidationResult,
    ModuleMergeConfig,
    ModuleMergeResult,
    TipoManejoDuplicados,
    TipoManejoErrores,
)
from .exceptions import (
    ConfigurationError,
    DataQualityError,
    GeoMergeError,
    ModuleMergeError,
    ValidationThresholdError,
)
from .geographic.patterns import GeoPatternDetector
from .geographic.strategies import DuplicateStrategyFactory
from .geographic.validators import GeoDataQualityValidator, TerritorialValidator, UbigeoValidator
from .modules.merger import ENAHOModuleMerger
from .modules.validator import ModuleValidator

# Importaciones opcionales del loader principal con fallback robusto
try:
    from ..loader import CacheManager, ENAHOConfig, log_performance, setup_logging

    LOADER_AVAILABLE = True
except ImportError:
    LOADER_AVAILABLE = False
    # Fallback completo para uso independiente
    from dataclasses import dataclass

    @dataclass(frozen=True)
    class ENAHOConfig:
        """Configuración fallback para uso independiente"""

        cache_dir: str = ".enaho_cache"
        use_cache: bool = True
        validate_data: bool = True

    def setup_logging(
        verbose: bool = True, structured: bool = False, log_file: Optional[str] = None
    ):
        """Setup de logging fallback"""
        logger = logging.getLogger("enaho_geo_merger")
        if not logger.handlers:
            handler = logging.StreamHandler()
            if structured:
                formatter = logging.Formatter(
                    '{"time":"%(asctime)s","level":"%(levelname)s","name":"%(name)s","message":"%(message)s"}'
                )
            else:
                formatter = logging.Formatter("[%(asctime)s] [%(levelname)s] %(name)s: %(message)s")
            handler.setFormatter(formatter)
            logger.addHandler(handler)

            if log_file:
                file_handler = logging.FileHandler(log_file)
                file_handler.setFormatter(formatter)
                logger.addHandler(file_handler)

            logger.setLevel(logging.INFO if verbose else logging.WARNING)
        return logger

    def log_performance(func):
        """Decorador de performance fallback"""

        def wrapper(*args, **kwargs):
            start_time = time.time()
            try:
                result = func(*args, **kwargs)
                elapsed = time.time() - start_time
                logger = logging.getLogger("enaho_geo_merger")
                logger.debug(f"⏱️ {func.__name__} ejecutado en {elapsed:.2f}s")
                return result
            except Exception as e:
                elapsed = time.time() - start_time
                logger = logging.getLogger("enaho_geo_merger")
                logger.error(f"❌ {func.__name__} falló después de {elapsed:.2f}s: {str(e)}")
                raise

        return wrapper

    # CacheManager será None si no está disponible
    CacheManager = None


class ENAHOGeoMerger:
    """
    Fusionador geográfico avanzado para datos INEI integrado con enahopy.
    EXTENDIDO con capacidades de merge entre módulos ENAHO.

    Proporciona funcionalidades completas para fusionar datos con información
    geográfica, validación de UBIGEO, detección automática de patrones,
    estrategias flexibles de manejo de duplicados, y merge entre módulos ENAHO.

    Attributes:
        config: Configuración general del sistema
        geo_config: Configuración específica para merge geográfico
        module_config: Configuración para merge de módulos
        logger: Logger configurado
        cache_enabled: Si el cache está habilitado y disponible

    Example:
        >>> from enahopy.merger import ENAHOGeoMerger
        >>> merger = ENAHOGeoMerger(verbose=True)
        >>> result_df, validation = merger.merge_geographic_data(df1, df2)
    """

    def __init__(self,
                 module_config: Optional[ModuleMergeConfig] = None,
                 verbose: bool = True):
        """
        Inicializa el merger
        """
        self.module_config = module_config or ModuleMergeConfig()
        self.verbose = verbose
        self.logger = self._setup_logger()

        # Inicializar el merger de módulos
        self.module_merger = ENAHOModuleMerger(self.module_config, self.logger)

        if self.verbose:
            self.logger.info("ENAHOGeoMerger inicializado correctamente")

    def _setup_logger(self) -> logging.Logger:
        """Configura el logger"""
        logger = logging.getLogger('enaho_geo_merger')
        if not logger.handlers:
            handler = logging.StreamHandler()
            formatter = logging.Formatter(
                '[%(asctime)s] [%(levelname)s] %(name)s: %(message)s'
            )
            handler.setFormatter(formatter)
            logger.addHandler(handler)
            logger.setLevel(logging.INFO if self.verbose else logging.WARNING)
        return logger

    def _validate_configurations(self):
        """
        Valida todas las configuraciones iniciales.

        Raises:
            ConfigurationError: Si alguna configuración es inválida
        """
        errors = []

        # Validar geo_config
        if self.geo_config.chunk_size <= 0:
            errors.append("chunk_size debe ser mayor que 0")

        if self.geo_config.chunk_size > 1000000:
            warnings.warn(
                f"chunk_size muy grande ({self.geo_config.chunk_size}), "
                "puede causar problemas de memoria",
                ResourceWarning,
            )

        if self.geo_config.manejo_duplicados == TipoManejoDuplicados.AGGREGATE:
            if not self.geo_config.funciones_agregacion:
                errors.append(
                    "funciones_agregacion es requerido cuando manejo_duplicados es AGGREGATE"
                )

        if self.geo_config.manejo_duplicados == TipoManejoDuplicados.BEST_QUALITY:
            if not self.geo_config.columna_calidad:
                errors.append(
                    "columna_calidad es requerido cuando manejo_duplicados es BEST_QUALITY"
                )

        # Validar module_config
        if self.module_config.min_match_rate < 0 or self.module_config.min_match_rate > 1:
            errors.append("min_match_rate debe estar entre 0 y 1")

        if self.module_config.max_conflicts_allowed < 0:
            errors.append("max_conflicts_allowed debe ser no negativo")

        if errors:
            raise ConfigurationError(f"Configuración inválida: {'; '.join(errors)}")

    def _setup_cache(self):
        """Configura el cache de manera segura verificando disponibilidad."""
        self.cache_manager = None
        self.cache_enabled = False

        if hasattr(self.config, "use_cache") and self.config.use_cache:
            if CacheManager is not None:
                try:
                    self.cache_manager = CacheManager(cache_dir=self.config.cache_dir)
                    self.cache_enabled = True
                    self.logger.info("Cache habilitado y configurado")
                except Exception as e:
                    self.logger.warning(
                        f"No se pudo inicializar el cache: {str(e)}. " "Continuando sin cache."
                    )
            else:
                if self.geo_config.usar_cache:
                    self.logger.warning(
                        "CacheManager no disponible. Instale el módulo loader "
                        "para habilitar cache. Continuando sin cache."
                    )

    def _initialize_geographic_components(self):
        """Inicializa componentes geográficos con manejo de errores."""
        try:
            self.ubigeo_validator = UbigeoValidator(self.logger)
            self.territorial_validator = TerritorialValidator(self.logger)
            self.quality_validator = GeoDataQualityValidator(self.logger)
            self.pattern_detector = GeoPatternDetector(self.logger)
            self.logger.debug("Componentes geográficos inicializados")
        except Exception as e:
            self.logger.error(f"Error inicializando componentes geográficos: {str(e)}")
            raise

    def _initialize_module_components(self):
        """Inicializa componentes de módulos con manejo de errores."""
        try:
            self.module_merger = ENAHOModuleMerger(self.module_config, self.logger)
            self.module_validator = ModuleValidator(self.module_config, self.logger)
            self.logger.debug("Componentes de módulos inicializados")
        except Exception as e:
            self.logger.error(f"Error inicializando componentes de módulos: {str(e)}")
            raise

    @log_performance
    def validate_geographic_data(
        self,
        df: pd.DataFrame,
        columna_ubigeo: str = "ubigeo",
        validate_territory: bool = True,
        validate_quality: bool = True,
    ) -> GeoValidationResult:
        """
        Valida datos geográficos con checks comprehensivos.

        Args:
            df: DataFrame a validar
            columna_ubigeo: Nombre de la columna con códigos UBIGEO
            validate_territory: Si validar consistencia territorial
            validate_quality: Si validar calidad de datos

        Returns:
            GeoValidationResult con métricas detalladas de validación

        Raises:
            ValueError: Si el DataFrame está vacío o no tiene la columna especificada

        Example:
            >>> validation = merger.validate_geographic_data(df, 'ubigeo')
            >>> print(f"Cobertura: {validation.coverage_percentage}%")
        """
        # Validaciones de entrada
        if df is None or df.empty:
            self.logger.error("DataFrame vacío proporcionado para validación")
            return GeoValidationResult(
                is_valid=False,
                total_records=0,
                valid_ubigeos=0,
                invalid_ubigeos=0,
                duplicate_ubigeos=0,
                missing_coordinates=0,
                territorial_inconsistencies=0,
                coverage_percentage=0.0,
                errors=["DataFrame vacío"],
                warnings=[],
                quality_metrics={},
            )

        if columna_ubigeo not in df.columns:
            raise ValueError(f"Columna '{columna_ubigeo}' no encontrada en el DataFrame")

        self.logger.info(f"Validando datos geográficos: {len(df)} registros")

        total_records = len(df)
        errors = []
        warnings = []

        # Manejar caso de DataFrame con solo NaN
        if df[columna_ubigeo].isna().all():
            self.logger.warning("Todos los valores de UBIGEO son NaN")
            return GeoValidationResult(
                is_valid=False,
                total_records=total_records,
                valid_ubigeos=0,
                invalid_ubigeos=0,
                duplicate_ubigeos=0,
                missing_coordinates=0,
                territorial_inconsistencies=0,
                coverage_percentage=0.0,
                errors=["Todos los valores de UBIGEO son NaN"],
                warnings=["No hay datos geográficos válidos para procesar"],
                quality_metrics={"data_completeness": 0.0},
            )

        # Validación de UBIGEO con manejo de NaN
        non_nan_mask = df[columna_ubigeo].notna()
        non_nan_count = non_nan_mask.sum()

        if non_nan_count > 0:
            valid_mask, validation_errors = self.ubigeo_validator.validar_serie_ubigeos(
                df.loc[non_nan_mask, columna_ubigeo], self.geo_config.tipo_validacion_ubigeo
            )
            valid_ubigeos = valid_mask.sum()
            invalid_ubigeos = non_nan_count - valid_ubigeos
        else:
            valid_ubigeos = 0
            invalid_ubigeos = 0
            validation_errors = []

        # Agregar NaN a los inválidos
        invalid_ubigeos += total_records - non_nan_count

        if validation_errors:
            errors.extend(validation_errors[:5])  # Limitar errores mostrados
            if len(validation_errors) > 5:
                errors.append(f"...y {len(validation_errors) - 5} errores más")

        # Detectar duplicados (solo en valores no-NaN)
        if non_nan_count > 0:
            duplicates_mask = df.loc[non_nan_mask, columna_ubigeo].duplicated(keep=False)
            duplicate_ubigeos = duplicates_mask.sum()
        else:
            duplicate_ubigeos = 0

        if duplicate_ubigeos > 0:
            unique_duplicates = df.loc[non_nan_mask][duplicates_mask][columna_ubigeo].nunique()
            warnings.append(
                f"{duplicate_ubigeos} registros con UBIGEO duplicado ({unique_duplicates} valores únicos)"
            )

        # Validación territorial
        territorial_inconsistencies = 0
        if validate_territory and valid_ubigeos > 0:
            valid_data = df[non_nan_mask & valid_mask]
            if not valid_data.empty:
                territorial_issues = self.territorial_validator.validar_jerarquia_territorial(
                    valid_data, columna_ubigeo
                )
                territorial_inconsistencies = len(territorial_issues)
                if territorial_inconsistencies > 0:
                    warnings.append(
                        f"{territorial_inconsistencies} inconsistencias territoriales detectadas"
                    )

        # Validación de coordenadas
        missing_coordinates = 0
        coord_columns = ["latitud", "longitud", "lat", "lon", "x", "y"]
        found_coords = [col for col in coord_columns if col in df.columns]

        if found_coords and self.geo_config.validar_coordenadas:
            for coord_col in found_coords:
                missing_coordinates += df[coord_col].isna().sum()

            if missing_coordinates > 0:
                coord_coverage = (
                    (
                        (len(found_coords) * total_records - missing_coordinates)
                        / (len(found_coords) * total_records)
                        * 100
                    )
                    if total_records > 0
                    else 0
                )
                warnings.append(f"Cobertura de coordenadas: {coord_coverage:.1f}%")

        # Calcular métricas de calidad
        # Corregir división por cero
        coverage_percentage = (valid_ubigeos / total_records * 100) if total_records > 0 else 0.0

        quality_metrics = {
            "completeness": (non_nan_count / total_records * 100) if total_records > 0 else 0.0,
            "validity": (valid_ubigeos / non_nan_count * 100) if non_nan_count > 0 else 0.0,
            "uniqueness": (
                ((non_nan_count - duplicate_ubigeos) / non_nan_count * 100)
                if non_nan_count > 0
                else 100.0
            ),
            "consistency": (
                ((total_records - territorial_inconsistencies) / total_records * 100)
                if total_records > 0
                else 100.0
            ),
        }

        # Determinar si es válido con umbrales ajustables
        min_coverage = getattr(self.geo_config, "min_coverage_threshold", 80.0)
        min_uniqueness = getattr(self.geo_config, "min_uniqueness_threshold", 95.0)

        is_valid = (
            coverage_percentage >= min_coverage
            and quality_metrics["uniqueness"] >= min_uniqueness
            and territorial_inconsistencies == 0
        )

        result = GeoValidationResult(
            is_valid=is_valid,
            total_records=total_records,
            valid_ubigeos=valid_ubigeos,
            invalid_ubigeos=invalid_ubigeos,
            duplicate_ubigeos=duplicate_ubigeos,
            missing_coordinates=missing_coordinates,
            territorial_inconsistencies=territorial_inconsistencies,
            coverage_percentage=coverage_percentage,
            errors=errors,
            warnings=warnings,
            quality_metrics=quality_metrics,
        )

        self.logger.info(f"Validación completada - Cobertura: {coverage_percentage:.1f}%")
        return result

    def _handle_duplicates(self, df: pd.DataFrame, columna_union: str) -> pd.DataFrame:
        """
        Maneja duplicados usando la estrategia configurada.

        Args:
            df: DataFrame con posibles duplicados
            columna_union: Columna para identificar duplicados

        Returns:
            DataFrame sin duplicados según la estrategia

        Raises:
            GeoMergeError: Si la estrategia es ERROR y hay duplicados
        """
        if df.empty:
            return df

        # Identificar duplicados (excluyendo NaN)
        non_nan_mask = df[columna_union].notna()
        if not non_nan_mask.any():
            return df

        duplicates_mask = df[columna_union].duplicated(keep=False)

        if not duplicates_mask.any():
            return df

        n_duplicates = duplicates_mask.sum()
        self.logger.info(f"Encontrados {n_duplicates} registros duplicados en '{columna_union}'")

        if self.geo_config.manejo_duplicados == TipoManejoDuplicados.ERROR:
            ubigeos_duplicados = df[duplicates_mask][columna_union].unique()
            raise GeoMergeError(
                f"Se encontraron {n_duplicates} duplicados en '{columna_union}'. "
                f"UBIGEOs afectados: {list(ubigeos_duplicados[:5])}... "
                f"Use otra estrategia de manejo_duplicados si desea procesarlos."
            )

        try:
            strategy = DuplicateStrategyFactory.create_strategy(
                self.geo_config.manejo_duplicados, self.logger
            )
            return strategy.handle_duplicates(df, columna_union, self.geo_config)
        except Exception as e:
            self.logger.error(f"Error manejando duplicados: {str(e)}")
            raise

    @log_performance
    def merge_geographic_data(
        self,
        df_principal: pd.DataFrame,
        df_geografia: pd.DataFrame,
        columnas_geograficas: Optional[Dict[str, str]] = None,
        columna_union: Optional[str] = None,
        validate_before_merge: bool = None,
    ) -> Tuple[pd.DataFrame, GeoValidationResult]:
        """
        Fusiona datos principales con información geográfica.

        Args:
            df_principal: DataFrame principal con datos a enriquecer
            df_geografia: DataFrame con información geográfica
            columnas_geograficas: Mapeo de columnas a incluir del df_geografia
            columna_union: Columna para realizar el merge (default: desde config)
            validate_before_merge: Si validar datos antes del merge (default: desde config)

        Returns:
            Tupla (DataFrame fusionado, GeoValidationResult)

        Raises:
            ValueError: Si los DataFrames están vacíos o faltan columnas requeridas
            GeoMergeError: Si hay errores durante el merge
            DataQualityError: Si la calidad de datos no cumple los umbrales

        Example:
            >>> df_result, validation = merger.merge_geographic_data(
            ...     df_principal=df_data,
            ...     df_geografia=df_geo,
            ...     columna_union='ubigeo'
            ... )
            >>> print(f"Registros fusionados: {len(df_result)}")
        """
        # Validaciones de entrada exhaustivas
        if df_principal is None or df_principal.empty:
            raise ValueError("df_principal no puede estar vacío")

        if df_geografia is None or df_geografia.empty:
            raise ValueError("df_geografia no puede estar vacío")

        columna_union = columna_union or self.geo_config.columna_union
        validate_before_merge = (
            validate_before_merge
            if validate_before_merge is not None
            else self.geo_config.validar_formato_ubigeo
        )

        # Verificar que la columna de unión existe en ambos DataFrames
        if columna_union not in df_principal.columns:
            raise ValueError(
                f"Columna '{columna_union}' no encontrada en df_principal. "
                f"Columnas disponibles: {list(df_principal.columns[:10])}..."
            )

        if columna_union not in df_geografia.columns:
            raise ValueError(
                f"Columna '{columna_union}' no encontrada en df_geografia. "
                f"Columnas disponibles: {list(df_geografia.columns[:10])}..."
            )

        self.logger.info(
            f"Iniciando merge geográfico: "
            f"{len(df_principal)} registros principales × "
            f"{len(df_geografia)} registros geográficos"
        )

        # Validar tipos de datos de las columnas de unión
        self._validate_merge_column_types(df_principal, df_geografia, columna_union)

        # Detectar columnas geográficas si no se especifican
        if columnas_geograficas is None:
            self.logger.info("columnas geográficas automáticamente...")
            columnas_geograficas = self.pattern_detector.detectar_columnas_geograficas(
                df_geografia, confidence_threshold=0.7
            )
            self.logger.info(f"Columnas detectadas: {list(columnas_geograficas.keys())}")

        # Validación previa si está configurada
        validation_result = None
        if validate_before_merge:
            validation_result = self.validate_geographic_data(
                df_geografia,
                columna_union,
                validate_territory=self.geo_config.validar_consistencia_territorial,
                validate_quality=self.geo_config.generar_reporte_calidad,
            )

            if (
                not validation_result.is_valid
                and self.geo_config.manejo_errores == TipoManejoErrores.RAISE
            ):
                raise DataQualityError(
                    f"Validación de datos geográficos falló: {validation_result.errors}",
                    validation_result=validation_result,
                )

        # Preparar DataFrames para merge
        df_geo_clean = self._prepare_geographic_df(
            df_geografia, columna_union, columnas_geograficas
        )

        # Manejar duplicados
        df_geo_clean = self._handle_duplicates(df_geo_clean, columna_union)

        # Realizar merge con manejo de memoria optimizado
        if self.geo_config.optimizar_memoria and len(df_principal) > self.geo_config.chunk_size:
            result_df = self._merge_by_chunks(df_principal, df_geo_clean, columna_union)
        else:
            result_df = self._merge_simple(df_principal, df_geo_clean, columna_union)

        # Manejo de valores faltantes
        if self.geo_config.valor_faltante is not None:
            geo_columns = [col for col in result_df.columns if col in columnas_geograficas.values()]
            for col in geo_columns:
                result_df[col] = result_df[col].fillna(self.geo_config.valor_faltante)

        # Generar reporte final
        if validation_result is None:
            validation_result = self._generate_merge_report(
                df_principal, df_geografia, result_df, columna_union
            )

        self.logger.info(
            f"Merge completado: {len(result_df)} registros, " f"{result_df.shape[1]} columnas"
        )

        return result_df, validation_result

    def _validate_merge_column_types(self, df1: pd.DataFrame, df2: pd.DataFrame, column: str):
        """
        Valida y corrige tipos de datos de columnas de merge.

        Args:
            df1, df2: DataFrames a fusionar
            column: Columna de merge

        Raises:
            ValueError: Si los tipos son incompatibles y no se pueden convertir
        """
        type1 = df1[column].dtype
        type2 = df2[column].dtype

        if type1 != type2:
            self.logger.warning(
                f"⚠️ Tipos de datos diferentes en '{column}': "
                f"{type1} vs {type2}. Intentando convertir..."
            )

            # Intentar conversión a string si son tipos diferentes
            try:
                if pd.api.types.is_numeric_dtype(type1) and pd.api.types.is_string_dtype(type2):
                    df1[column] = df1[column].astype(str)
                elif pd.api.types.is_string_dtype(type1) and pd.api.types.is_numeric_dtype(type2):
                    df2[column] = df2[column].astype(str)
                else:
                    # Convertir ambos a string como último recurso
                    df1[column] = df1[column].astype(str)
                    df2[column] = df2[column].astype(str)

                self.logger.info(f"✅ Tipos convertidos exitosamente para '{column}'")
            except Exception as e:
                raise ValueError(
                    f"No se pudieron compatibilizar los tipos de datos para '{column}': {str(e)}"
                )

    def _prepare_geographic_df(
        self, df: pd.DataFrame, columna_union: str, columnas_geograficas: Dict[str, str]
    ) -> pd.DataFrame:
        """
        Prepara DataFrame geográfico para merge.

        Args:
            df: DataFrame geográfico
            columna_union: Columna de unión
            columnas_geograficas: Columnas a incluir

        Returns:
            DataFrame preparado
        """
        # Seleccionar columnas relevantes
        columns_to_keep = [columna_union]

        for orig_col, new_col in columnas_geograficas.items():
            if orig_col in df.columns:
                columns_to_keep.append(orig_col)
            else:
                self.logger.warning(f"⚠️ Columna '{orig_col}' no encontrada en df_geografia")

        df_clean = df[columns_to_keep].copy()

        # Renombrar columnas si es necesario
        rename_dict = {}
        for orig_col, new_col in columnas_geograficas.items():
            if orig_col in df_clean.columns and orig_col != new_col:
                rename_dict[orig_col] = new_col

        if rename_dict:
            df_clean = df_clean.rename(columns=rename_dict)
            self.logger.debug(f"Columnas renombradas: {rename_dict}")

        # Aplicar prefijos/sufijos si están configurados
        if self.geo_config.prefijo_columnas or self.geo_config.sufijo_columnas:
            rename_dict = {}
            for col in df_clean.columns:
                if col != columna_union:  # No renombrar la columna de unión
                    new_name = (
                        f"{self.geo_config.prefijo_columnas}{col}{self.geo_config.sufijo_columnas}"
                    )
                    rename_dict[col] = new_name

            if rename_dict:
                df_clean = df_clean.rename(columns=rename_dict)

        return df_clean

    def _merge_simple(self, df1: pd.DataFrame, df2: pd.DataFrame, on: str) -> pd.DataFrame:
        """
        Realiza merge simple entre dos DataFrames.

        Args:
            df1, df2: DataFrames a fusionar
            on: Columna de unión

        Returns:
            DataFrame fusionado
        """
        try:
            return pd.merge(df1, df2, on=on, how="left", validate="m:1")
        except pd.errors.MergeError as e:
            self.logger.error(f"Error en merge: {str(e)}")
            # Intentar merge sin validación
            self.logger.warning("Reintentando merge sin validación m:1...")
            return pd.merge(df1, df2, on=on, how="left")

    def _merge_by_chunks(self, df1: pd.DataFrame, df2: pd.DataFrame, on: str) -> pd.DataFrame:
        """
        Realiza merge por chunks para optimizar memoria.

        Args:
            df1, df2: DataFrames a fusionar
            on: Columna de unión

        Returns:
            DataFrame fusionado
        """
        chunk_size = self.geo_config.chunk_size
        n_chunks = (len(df1) + chunk_size - 1) // chunk_size

        self.logger.info(f"📦 Procesando en {n_chunks} chunks de {chunk_size} registros")

        chunks_results = []
        for i in range(n_chunks):
            start_idx = i * chunk_size
            end_idx = min((i + 1) * chunk_size, len(df1))

            chunk = df1.iloc[start_idx:end_idx]
            chunk_merged = pd.merge(chunk, df2, on=on, how="left")
            chunks_results.append(chunk_merged)

            if (i + 1) % 10 == 0:
                self.logger.debug(f"Procesados {i + 1}/{n_chunks} chunks")

        result = pd.concat(chunks_results, ignore_index=True)
        self.logger.info(f"✅ Chunks combinados: {len(result)} registros")

        return result

    def _generate_merge_report(
        self,
        df_original: pd.DataFrame,
        df_geo: pd.DataFrame,
        df_result: pd.DataFrame,
        columna_union: str,
    ) -> GeoValidationResult:
        """
        Genera reporte detallado del merge.

        Args:
            df_original: DataFrame original
            df_geo: DataFrame geográfico
            df_result: DataFrame resultado
            columna_union: Columna de unión

        Returns:
            GeoValidationResult con métricas del merge
        """
        total_records = len(df_result)

        # Calcular métricas de cobertura
        non_null_geo = df_result[columna_union].notna().sum()
        coverage_percentage = (non_null_geo / total_records * 100) if total_records > 0 else 0.0

        # Detectar registros sin match
        new_cols = set(df_result.columns) - set(df_original.columns)
        missing_geo = 0

        for col in new_cols:
            missing_geo = max(missing_geo, df_result[col].isna().sum())

        quality_metrics = {
            "original_records": len(df_original),
            "geographic_records": len(df_geo),
            "merged_records": total_records,
            "coverage": coverage_percentage,
            "new_columns": len(new_cols),
            "missing_matches": missing_geo,
        }

        warnings = []
        if missing_geo > 0:
            warnings.append(f"{missing_geo} registros sin información geográfica")

        return GeoValidationResult(
            is_valid=True,
            total_records=total_records,
            valid_ubigeos=non_null_geo,
            invalid_ubigeos=total_records - non_null_geo,
            duplicate_ubigeos=0,
            missing_coordinates=0,
            territorial_inconsistencies=0,
            coverage_percentage=coverage_percentage,
            errors=[],
            warnings=warnings,
            quality_metrics=quality_metrics,
        )

    # =====================================================
    # MÉTODOS DE MERGE DE MÓDULOS
    # =====================================================

    @log_performance
    def merge_multiple_modules(self,
                               modules_dict: Dict[str, pd.DataFrame],
                               base_module: str,
                               config: Optional[ModuleMergeConfig] = None) -> ModuleMergeResult:
        """
        Fusiona múltiples módulos ENAHO con corrección del bug

        Args:
            modules_dict: Diccionario con módulos {código: DataFrame}
            base_module: Módulo base para el merge
            config: Configuración opcional

        Returns:
            ModuleMergeResult con el resultado del merge
        """
        start_time = time.time()
        config = config or self.module_config

        try:
            # Log inicio
            self.logger.info(f"Iniciando merge de {len(modules_dict)} módulos con base '{base_module}'")

            # Validar módulos
            self._validate_modules(modules_dict, base_module)

            # Ordenar módulos para merge
            merge_order = self._determine_merge_order(modules_dict, base_module)
            self.logger.info(f"Orden de merge: {' → '.join(merge_order)}")

            # Inicializar resultado base
            base_df = modules_dict[base_module].copy()
            merged_df = base_df

            # Acumuladores para el reporte
            all_warnings = []
            all_conflicts = 0
            all_unmatched_left = 0
            all_unmatched_right = 0
            merge_reports = []

            # Fusionar módulos uno por uno
            for module_code in merge_order[1:]:  # Excluir el base que ya tenemos
                self.logger.info(f"Agregando módulo {module_code}")

                try:
                    # Realizar merge individual
                    result = self.module_merger.merge_modules(
                        merged_df,
                        modules_dict[module_code],
                        base_module if merged_df is base_df else "merged",
                        module_code
                    )

                    # Actualizar DataFrame fusionado
                    merged_df = result.merged_df

                    # ✅ CORRECCIÓN DEL BUG: usar validation_warnings en lugar de warnings
                    all_warnings.extend(result.validation_warnings)  # AQUÍ ESTABA EL BUG

                    # Acumular estadísticas
                    all_conflicts += result.conflicts_resolved
                    all_unmatched_left += result.unmatched_left
                    all_unmatched_right += result.unmatched_right

                    # Guardar reporte individual
                    merge_reports.append({
                        'module': module_code,
                        'report': result.merge_report,
                        'quality_score': result.quality_score
                    })

                    self.logger.info(
                        f"Merge completado: {len(merged_df)} registros finales "
                        f"(Calidad: {result.quality_score:.1%})"
                    )

                except Exception as e:
                    self.logger.error(f"Error fusionando módulo {module_code}: {str(e)}")
                    raise MergeValidationError(f"Fallo en merge de módulo {module_code}: {str(e)}")

            # Calcular calidad total
            total_quality = self._calculate_total_quality(merge_reports)

            # Crear reporte consolidado
            elapsed_time = time.time() - start_time

            merge_report = {
                'modules_merged': list(modules_dict.keys()),
                'base_module': base_module,
                'merge_order': merge_order,
                'total_records': len(merged_df),
                'individual_reports': merge_reports,
                'elapsed_time': elapsed_time,
                'timestamp': datetime.now().isoformat()
            }

            # Crear resultado final
            final_result = ModuleMergeResult(
                merged_df=merged_df,
                merge_report=merge_report,
                conflicts_resolved=all_conflicts,
                unmatched_left=all_unmatched_left,
                unmatched_right=all_unmatched_right,
                validation_warnings=all_warnings,  # Usar el nombre correcto del atributo
                quality_score=total_quality
            )

            self.logger.info(
                f"merge_multiple_modules completado en {elapsed_time:.2f}s "
                f"con calidad total: {total_quality:.1%}"
            )

            return final_result

        except Exception as e:
            elapsed_time =  time.time() - start_time
            self.logger.error(
                f"merge_multiple_modules falló después de {elapsed_time:.2f}s: {str(e)}"
            )
            raise

    def _validate_modules(self, modules_dict: Dict[str, pd.DataFrame], base_module: str):
        """Valida que los módulos sean compatibles para merge"""
        self.logger.info(f"Validando compatibilidad de {len(modules_dict)} módulos")

        if base_module not in modules_dict:
            raise ValueError(f"Módulo base '{base_module}' no encontrado")

        if len(modules_dict) < 2:
            raise ValueError("Se requieren al menos 2 módulos para fusionar")

        # Validar que todos sean DataFrames
        for code, df in modules_dict.items():
            if not isinstance(df, pd.DataFrame):
                raise TypeError(f"Módulo {code} no es un DataFrame")
            if df.empty:
                raise ValueError(f"Módulo {code} está vacío")

    def _determine_merge_order(self,
                               modules_dict: Dict[str, pd.DataFrame],
                               base_module: str) -> List[str]:
        """
        Determina el orden óptimo de merge
        Prioriza: base → sumaria → otros módulos por tamaño
        """
        modules = list(modules_dict.keys())
        modules.remove(base_module)

        # Ordenar por prioridad y tamaño
        def get_priority(module_code):
            priorities = {'34': 1, '02': 2, '01': 3}  # sumaria, personas, hogar
            return priorities.get(module_code, 99)

        modules.sort(key=lambda x: (get_priority(x), -len(modules_dict[x])))

        return [base_module] + modules

    def _calculate_total_quality(self, merge_reports: List[Dict]) -> float:
        """Calcula la calidad promedio ponderada de todos los merges"""
        if not merge_reports:
            return 0.0

        total_score = sum(r['quality_score'] for r in merge_reports)
        return total_score / len(merge_reports)

    @log_performance
    def merge_modules_with_geography(
        self,
        modules_dict: Dict[str, pd.DataFrame],
        df_geografia: pd.DataFrame,
        base_module: str = "34",
        merge_config: Optional[ModuleMergeConfig] = None,
        geo_config: Optional[GeoMergeConfiguration] = None,
    ) -> Tuple[pd.DataFrame, Dict[str, Any]]:
        """
        Combina merge de módulos con información geográfica.

        Args:
            modules_dict: Diccionario de módulos ENAHO
            df_geografia: DataFrame con información geográfica
            base_module: Módulo base para el merge
            merge_config: Configuración para merge de módulos
            geo_config: Configuración para merge geográfico

        Returns:
            Tupla (DataFrame final, reporte combinado)

        Raises:
            ValueError: Si los inputs son inválidos
            ModuleMergeError: Si falla el merge de módulos
            GeoMergeError: Si falla el merge geográfico

        Example:
            >>> modules = {"34": df_sumaria, "01": df_vivienda}
            >>> df_geo = pd.DataFrame({'ubigeo': [...], 'distrito': [...]})
            >>> result, report = merger.merge_modules_with_geography(
            ...     modules, df_geo, base_module="34"
            ... )
        """
        # Validaciones
        if not modules_dict:
            raise ValueError("modules_dict no puede estar vacío")

        if df_geografia is None or df_geografia.empty:
            raise ValueError("df_geografia no puede estar vacío")

        self.logger.info("🌍 Iniciando merge combinado: módulos + geografía")

        # 1. Merge entre módulos
        module_result = self.merge_multiple_modules(
            modules_dict, base_module, merge_config, validate_compatibility=True
        )

        self.logger.info(f"📊 Módulos combinados: {len(module_result.merged_df)} registros")

        # 2. Merge con información geográfica
        # Usar configuración específica si se proporciona
        original_geo_config = self.geo_config
        if geo_config:
            self.geo_config = geo_config

        try:
            geo_result, geo_validation = self.merge_geographic_data(
                df_principal=module_result.merged_df,
                df_geografia=df_geografia,
                validate_before_merge=True,
            )
        finally:
            # Restaurar configuración original
            self.geo_config = original_geo_config

        # 3. Combinar reportes
        combined_report = {
            "module_merge": {
                "modules_processed": module_result.modules_merged,
                "conflicts_resolved": module_result.conflicts_resolved,
                "warnings": module_result.warnings,
                "quality_metrics": module_result.quality_metrics,
            },
            "geographic_merge": {
                "validation": (
                    geo_validation.to_dict()
                    if hasattr(geo_validation, "to_dict")
                    else vars(geo_validation)
                ),
                "final_records": len(geo_result),
                "coverage": geo_validation.coverage_percentage,
            },
            "overall_quality": self._assess_combined_quality(geo_result, module_result),
            "processing_summary": {
                "modules_processed": len(modules_dict),
                "base_module": base_module,
                "final_shape": geo_result.shape,
                "merge_sequence": " → ".join(module_result.modules_merged),
                "geographic_coverage": geo_validation.coverage_percentage,
            },
        }

        self.logger.info(
            f"✅ Merge combinado completado: {geo_result.shape[0]} registros, "
            f"{geo_result.shape[1]} columnas"
        )

        return geo_result, combined_report

    def _assess_combined_quality(
        self, final_df: pd.DataFrame, module_result: ModuleMergeResult
    ) -> Dict[str, Any]:
        """
        Evalúa la calidad general del merge combinado.

        Args:
            final_df: DataFrame final
            module_result: Resultado del merge de módulos

        Returns:
            Diccionario con métricas de calidad combinadas
        """
        # Calcular completitud general
        completeness = final_df.notna().sum().sum() / (final_df.shape[0] * final_df.shape[1]) * 100

        # Detectar columnas con alta proporción de NaN
        high_nan_cols = []
        for col in final_df.columns:
            nan_ratio = final_df[col].isna().mean()
            if nan_ratio > 0.5:  # Más del 50% NaN
                high_nan_cols.append((col, round(nan_ratio * 100, 1)))

        # Evaluar calidad general
        quality_score = completeness

        if module_result.conflicts_found > 0:
            quality_score -= (module_result.conflicts_found / len(final_df)) * 10

        if high_nan_cols:
            quality_score -= len(high_nan_cols) * 2

        quality_score = max(0, min(100, quality_score))  # Limitar entre 0 y 100

        return {
            "overall_score": round(quality_score, 2),
            "data_completeness": round(completeness, 2),
            "high_nan_columns": high_nan_cols[:10],  # Top 10 columnas con más NaN
            "total_conflicts": module_result.conflicts_found,
            "warnings_count": len(module_result.warnings),
            "recommendation": self._get_quality_recommendation(quality_score),
        }

    def _get_quality_recommendation(self, score: float) -> str:
        """
        Genera recomendación basada en el score de calidad.

        Args:
            score: Score de calidad (0-100)

        Returns:
            Recomendación textual
        """
        if score >= 90:
            return "Excelente calidad de datos. Listo para análisis."
        elif score >= 75:
            return "Buena calidad. Revisar columnas con valores faltantes."
        elif score >= 60:
            return "Calidad aceptable. Se recomienda validación adicional."
        elif score >= 40:
            return "Calidad baja. Revisar conflictos y datos faltantes."
        else:
            return "Calidad crítica. Se requiere limpieza de datos exhaustiva."

    def validate_module_compatibility(
        self, modules_dict: Dict[str, pd.DataFrame], merge_level: str = "hogar"
    ) -> Dict[str, Any]:
        """
        Valida compatibilidad entre múltiples módulos.

        Args:
            modules_dict: Diccionario de módulos
            merge_level: Nivel de merge deseado

        Returns:
            Diccionario con resultado de validación
        """
        self.logger.info(f"🔍 Validando compatibilidad de {len(modules_dict)} módulos")

        compatibility = {
            "is_compatible": True,
            "merge_level": merge_level,
            "errors": [],
            "warnings": [],
            "module_analysis": {},
        }

        # Verificar llaves requeridas según nivel
        if merge_level == "hogar":
            required_keys = ["conglome", "vivienda", "hogar"]
        else:  # persona
            required_keys = ["conglome", "vivienda", "hogar", "codperso"]

        for module_code, df in modules_dict.items():
            module_info = {
                "has_required_keys": True,
                "missing_keys": [],
                "record_count": len(df),
                "column_count": df.shape[1],
            }

            # Verificar llaves
            for key in required_keys:
                if key not in df.columns:
                    module_info["has_required_keys"] = False
                    module_info["missing_keys"].append(key)
                    compatibility["errors"].append(f"Módulo {module_code}: falta llave '{key}'")
                    compatibility["is_compatible"] = False
                elif df[key].isna().all():
                    compatibility["warnings"].append(
                        f"Módulo {module_code}: llave '{key}' completamente nula"
                    )

            compatibility["module_analysis"][module_code] = module_info

        # Verificar consistencia de llaves entre módulos
        if compatibility["is_compatible"]:
            base_module = list(modules_dict.keys())[0]
            base_df = modules_dict[base_module]

            for module_code, df in modules_dict.items():
                if module_code == base_module:
                    continue

                # Crear llaves compuestas
                base_keys = base_df[required_keys].apply(lambda x: "_".join(x.astype(str)), axis=1)
                module_keys = df[required_keys].apply(lambda x: "_".join(x.astype(str)), axis=1)

                # Calcular overlap
                common_keys = set(base_keys) & set(module_keys)
                overlap_percentage = (
                    (len(common_keys) / len(base_keys) * 100) if len(base_keys) > 0 else 0
                )

                if overlap_percentage < 50:
                    compatibility["warnings"].append(
                        f"Bajo overlap entre {base_module} y {module_code}: {overlap_percentage:.1f}%"
                    )

        return compatibility
