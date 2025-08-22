"""Dagster Kafka Integration Package

Provides Kafka integration for Dagster data pipelines with support for:
- JSON message consumption with optional schema validation
- Avro message consumption with Schema Registry support
- Protobuf message consumption with Schema Registry support
- Schema evolution validation and compatibility checking
- Confluent Connect integration for connector management and monitoring
- Production-grade error handling and recovery
- Comprehensive monitoring and alerting system
- High-performance caching, batching, and connection pooling
- Configurable consumer groups and connection settings
- Dead Letter Queue (DLQ) support for enterprise error handling
- Dagster Components for YAML-based configuration
"""

from .resources import KafkaResource
from .resources import SecurityProtocol, SaslMechanism
from .io_manager import KafkaIOManager
from dagster_kafka.connect import ConfluentConnectResource
from dagster_kafka.connect import create_connector_asset, create_connector_health_sensor, create_connector_health_monitoring
from .avro_io_manager import AvroKafkaIOManager, avro_kafka_io_manager
from .protobuf_io_manager import ProtobufKafkaIOManager, protobuf_kafka_io_manager, ProtobufSchemaManager, create_protobuf_kafka_io_manager
from .json_schema_io_manager import JSONSchemaKafkaIOManager, create_json_schema_kafka_io_manager
from .schema_evolution import SchemaEvolutionValidator, CompatibilityLevel
from .dlq import DLQStrategy, ErrorType, DLQConfiguration, DLQManager, create_dlq_manager, CircuitBreakerState
from .production_utils import (
    ProductionSchemaEvolutionManager, 
    RecoveryStrategy, 
    SchemaEvolutionMetrics,
    with_schema_evolution_monitoring
)
from .monitoring import (
    SchemaEvolutionMonitor,
    AlertSeverity,
    MetricType,
    Alert,
    Metric,
    slack_alert_handler,
    email_alert_handler
)
from .performance import (
    PerformanceOptimizer,
    HighPerformanceCache,
    BatchProcessor,
    ConnectionPool,
    CacheStrategy,
    BatchStrategy,
    PerformanceMetrics
)
from .component import KafkaComponent, KafkaConfig, ConsumerConfig, TopicConfig

__version__ = "1.3.1"  # Updated version for Confluent Connect release

__all__ = [
    "KafkaResource",
    "SecurityProtocol",
    "SaslMechanism",
    "KafkaIOManager",
    "AvroKafkaIOManager",
    "avro_kafka_io_manager",
    "ProtobufKafkaIOManager",
    "protobuf_kafka_io_manager",
    "ProtobufSchemaManager",
    "create_protobuf_kafka_io_manager",
    "JSONSchemaKafkaIOManager",
    "create_json_schema_kafka_io_manager",
    "SchemaEvolutionValidator",
    "CompatibilityLevel",
    "DLQStrategy",
    "ErrorType",
    "DLQConfiguration",
    "DLQManager",
    "create_dlq_manager",
    "CircuitBreakerState",
    "ProductionSchemaEvolutionManager",
    "RecoveryStrategy",
    "SchemaEvolutionMetrics",
    "with_schema_evolution_monitoring",
    "SchemaEvolutionMonitor",
    "AlertSeverity",
    "MetricType",
    "Alert",
    "Metric",
    "slack_alert_handler",
    "email_alert_handler",
    "PerformanceOptimizer",
    "HighPerformanceCache",
    "BatchProcessor",
    "ConnectionPool",
    "CacheStrategy",
    "BatchStrategy",
    "PerformanceMetrics",
    "KafkaComponent",
    "KafkaConfig", 
    "ConsumerConfig",
    "TopicConfig",
    "ConfluentConnectResource",
    "create_connector_asset",
    "create_connector_health_sensor",
    "create_connector_health_monitoring",
]