from pyspark.sql import SparkSession
import os
import json

class DatabricksPybrvmeta:
    def __init__(self, spark: SparkSession = None):
        """
        Initialize with or without Spark.
        If Spark is provided → Databricks mode.
        If not → Local mode.
        """
        if spark is not None:
            self.spark = spark.getActiveSession()
            self.engine_type = "databricks"
        else:
            self.spark = None
            self.engine_type = "local"

    def setup_pybrv_meta(self, database: str):
        """
        Create database, 'pybrv_meta' schema, and required tables for business rule validation metadata.
        """
        
        # Create database and schema
        self.spark.sql(f"CREATE SCHEMA IF NOT EXISTS {database}.pybrv_meta")

        # Drop if exists
        self.spark.sql(f"DROP TABLE IF EXISTS {database}.pybrv_meta.pybrv_business_rule_check_result")
        self.spark.sql(f"DROP TABLE IF EXISTS {database}.pybrv_meta.pybrv_data_parity_result")
        self.spark.sql(f"DROP TABLE IF EXISTS {database}.pybrv_meta.pybrv_metadata")
        self.spark.sql(f"DROP TABLE IF EXISTS {database}.pybrv_meta.pybrv_unique_rule_mapping")
        self.spark.sql(f"DROP TABLE IF EXISTS {database}.pybrv_meta.pydpc_attribute_mismatch_details")
        self.spark.sql(f"DROP TABLE IF EXISTS {database}.pybrv_meta.pydpc_attribute_result")
        self.spark.sql(f"DROP TABLE IF EXISTS {database}.pybrv_meta.pydpc_attribute_stats")
        self.spark.sql(f"DROP TABLE IF EXISTS {database}.pybrv_meta.pydpc_attribute_summary")
        self.spark.sql(f"DROP TABLE IF EXISTS {database}.pybrv_meta.pydpc_record_results")
        self.spark.sql(f"DROP TABLE IF EXISTS {database}.pybrv_meta.pydpc_rule_summary")
        self.spark.sql(f"DROP TABLE IF EXISTS {database}.pybrv_meta.sgp_test_result")

        # Create tables
        self.spark.sql(f"""
        CREATE TABLE {database}.pybrv_meta.pybrv_business_rule_check_result (
            batch_id Decimal (20, 0),
            unique_rule_identifier BIGINT,
            execution_id BIGINT,
            team_name STRING,
            rule_name STRING,
            data_domain STRING,
            table_checked STRING,
            severity STRING,
            rule_category STRING,
            bookmark_column_name STRING,
            bookmark_start_date DATE,
            bookmark_end_date DATE,
            status STRING,
            pass_record_count INT,
            fail_record_count INT,
            pass_percentage INT,
            threshold INT,
            failed_keys STRING,
            failed_query STRING,
            test_case_comments STRING,
            remarks STRING,
            last_modified_ts TIMESTAMP 
        )
        USING DELTA
        """)

        self.spark.sql(f"""
        CREATE TABLE {database}.pybrv_meta.pybrv_data_parity_result (
            unique_rule_identifier BIGINT,
            execution_id BIGINT,
            rule_name STRING,
            data_domain STRING,
            table_checked STRING,
            bookmark_column_name STRING,
            bookmark_column_value DATE,
            join_key_values STRING,
            metric_dim_values STRING,
            attribute_name STRING,
            attribute_value INT,
            comments STRING,
            last_modified_ts TIMESTAMP 
        )
        USING DELTA
        """)

        self.spark.sql(f"""
        CREATE TABLE {database}.pybrv_meta.pybrv_metadata (
            unique_rule_identifier BIGINT NOT NULL,
            bookmark_start_date DATE,
            bookmark_end_date DATE,
            last_modified_ts TIMESTAMP
        )
        USING DELTA
        """)

        self.spark.sql(f"""
        CREATE TABLE {database}.pybrv_meta.pybrv_unique_rule_mapping (
            unique_rule_identifier BIGINT NOT NULL,
            team_name STRING,
            data_domain STRING,
            rule_category STRING,
            rule_id INT,
            rule_name STRING,
            last_modified_ts TIMESTAMP 
        )
        USING DELTA
        """)

        self.spark.sql(f"""
        CREATE TABLE {database}.pybrv_meta.pydpc_attribute_mismatch_details (
            unique_rule_identifier BIGINT,
            execution_id BIGINT,
            rule_name STRING,
            data_domain STRING,
            table_name STRING,
            bookmark_column_name STRING,
            bookmark_column_value STRING,
            join_key_values MAP<STRING, STRING>,
            metric_dim_values MAP<STRING, STRING>,
            mismatch_type STRING,
            column_mismatch_flags MAP<STRING, STRING>,
            source_values MAP<STRING, STRING>,
            target_values MAP<STRING, STRING>,
            mismatched_columns STRING,
            comments STRING,
            last_modified_ts TIMESTAMP
        )
        USING DELTA
        """)

        self.spark.sql(f"""
        CREATE TABLE {database}.pybrv_meta.pydpc_attribute_result (
            execution_id BIGINT,
            unique_rule_identifier BIGINT,
            data_domain STRING,
            team_name STRING,
            inventory STRING,
            tool_name STRING,
            test_case_type STRING,
            test_name STRING,
            execution_datetime TIMESTAMP,
            gpid STRING,
            test_execution_link STRING,
            status INT,
            remarks STRING,
            bookmark_column_name STRING,
            bookmark_start_date DATE,
            bookmark_end_date DATE,
            metadata STRING,
            last_modified_ts TIMESTAMP,
            pos STRING 
        )
        USING DELTA
        """)


        self.spark.sql(f"""
        CREATE TABLE {database}.pybrv_meta.pydpc_attribute_stats (
            execution_id BIGINT,
            unique_rule_identifier BIGINT,
            data_domain STRING,
            rule_name STRING,
            table_checked STRING,
            execution_date DATE,
            key_date_column STRING,
            key_date_value DATE,
            field_name STRING,
            comments STRING,
            source_records BIGINT,
            target_records BIGINT,
            target_rows_matched BIGINT,
            source_attribute_count BIGINT,
            target_attribute_count BIGINT 
        )
        USING DELTA
        """)


        self.spark.sql(f"""
        CREATE TABLE {database}.pybrv_meta.pydpc_attribute_summary (
            data_domain STRING,
            rule_name STRING,
            table_name STRING,
            field_name STRING,
            source_total_records STRING,
            target_total_records STRING,
            target_attribute_found STRING,
            attributes_matched_perc STRING,
            threshold STRING,
            execution_id BIGINT,
            unique_rule_identifier BIGINT
        )
        USING DELTA
        """)

        self.spark.sql(f"""
        CREATE TABLE {database}.pybrv_meta.pydpc_record_results (
            unique_rule_identifier BIGINT,
            execution_id BIGINT,
            rule_name STRING,
            data_domain STRING,
            table_name STRING,
            bookmark_column_name STRING,
            bookmark_column_value DATE,
            join_key_values STRING,
            metric_dim_values STRING,
            attribute_name STRING,
            attribute_value BIGINT,
            comments STRING,
            last_modified_ts TIMESTAMP
        )
        USING DELTA
        """)


        self.spark.sql(f"""
        CREATE TABLE {database}.pybrv_meta.pydpc_rule_summary (
            batch_id Decimal (20, 0),
            start_date STRING,
            end_date STRING,
            data_domain STRING,
            rule_name STRING,
            table_name STRING,
            status STRING,
            source_records STRING,
            target_found STRING,
            percent_records_found STRING,
            target_rows_matched STRING,
            percent_rows_matched STRING,
            attributes_checked STRING,
            attributes_matched STRING,
            comments STRING,
            execution_id BIGINT,
            unique_rule_identifier BIGINT 
        )
        USING DELTA
        """)

        self.spark.sql(f"""
        CREATE TABLE {database}.pybrv_meta.sgp_test_result (
            id INT,
            data_domain STRING,
            team_name STRING,
            inventory STRING,
            tool_name STRING,
            test_case_type STRING,
            test_name STRING,
            execution_datetime TIMESTAMP,
            gpid STRING,
            test_execution_link STRING,
            status INT,
            remarks STRING,
            bookmark_column_name STRING,
            bookmark_start_date DATE,
            bookmark_end_date DATE,
            metadata STRING,
            last_modified_ts TIMESTAMP,
            pos STRING 
        )
        USING DELTA
        """)


   
        print(f"✅ All tables in `{database}.pybrv_meta` created successfully.")


    def create_business_rules_structure(self, base_path: str):
        """
        Creates the Business Rules folder and JSON file at given base_path.
        """
        structure = {
            "PYBRV": {
                "Configs": {
                    "json": {
                        "business_rules.json": {
                            "TEAM_NAME": "Data",
                            "TEAM_EMAIL": "team@xyzcompany.com",
                            "DOMAIN_NAME": "Transactions",
                            "RULE_CATEGORY_NAME": "BUSINESS_RULE_CHECK",
                            "DATABASE_NAME": "pybrv",
                            "ENGINE_TYPE": "databricks",
                            "RULES": [
                                {
                                    "RULE_ID": 1,
                                    "RULE_NAME": "unique_transactions_id_check",
                                    "RULE_CATEGORY": "Uniqueness",
                                    "SEVERITY": "Critical",
                                    "STOP_ON_FAIL_STATUS": "FALSE",
                                    "FAIL_SQL": f"{base_path}/PYBRV/Configs/sql/business_rules_sql/unique_transactionsid_fail.sql",
                                    "PASS_SQL": f"{base_path}/PYBRV/Configs/sql/business_rules_sql/unique_transactionsid_pass.sql",
                                    "TABLES_CHECKED": "sales_transactions",
                                    "INVENTORY": "Transactions Validator Rules",
                                    "COMMENTS": "Check if transactionID is unique.",
                                    "PASS_THRESHOLD": 100,
                                    "BOOKMARK_START_DATE": "2025-04-10",
                                    "DEFAULT_BOOKMARK_START_DATE": "2025-03-20"
                                }
                            ]
                        }
                    },
                    "sql": {
                        "business_rules_sql": {
                            "unique_transactionsid_fail.sql": """SELECT transactionID, COUNT(*) FROM samples.bakehouse.sales_transactions GROUP BY transactionID HAVING COUNT(*) > 1;""",
                            "unique_transactionsid_pass.sql": """SELECT transactionID, COUNT(*) FROM samples.bakehouse.sales_transactions GROUP BY transactionID HAVING COUNT(*) = 1;"""
                        }
                    }
                }
            }
        }

        self._create_items(base_path, structure)
        print(f"✅ Business Rules structure created at: {base_path}")

    def create_data_parity_structure(self, base_path: str):
        """
        Creates the Data Parity folder with JSON and SQL files.
        """
        structure = {
            "PYBRV": {
                "Configs": {
                    "json": {
                        "parity_checks.json": {
                            "TEAM_NAME": "DATA",
                            "TEAM_EMAIL": "team@xyzcompany.com",
                            "RULE_CATEGORY_NAME": "DATA_PARITY_CHECK",
                            "ENGINE_TYPE": "databricks",
                            "DATA_DOMAIN": "DATA",
                            "DOMAIN_NAME": "DATA",
                            "DATABASE_NAME": "pybrv",
                            "SCHEMA": "pybrv_meta",
                            "RULES": [
                                {
                                    "RULE_ID": 1,
                                    "RULE_NAME": "DEMO-EMP-DATA-CHECK",
                                    "SOURCE_SQL": f"{base_path}/PYBRV/Configs/sql/data_parity_sql/source.sql",
                                    "TARGET_SQL": f"{base_path}/PYBRV/Configs/sql/data_parity_sql/target.sql",
                                    "JOIN_DIMENSIONS": "transactionId",
                                    "INVENTORY": "Demo Tables",
                                    "TABLE_NAME": "sales_transactions",
                                    "COMMENTS": "Running only Demo tables",
                                    "METRIC_DIMENSIONS": "transactionId",
                                    "THRESHOLD": 95,
                                    "POS": "Demo",
                                    "CUST_EXP_TESTING": 1,
                                    "RECORD_THRESHOLD": 95
                                }
                            ]
                        }
                    },
                    "sql": {
                        "data_parity_sql": {
                            "source.sql": """SELECT * FROM samples.bakehouse.sales_transactions LIMIT 100;""",
                            "target.sql": """SELECT * FROM samples.bakehouse.sales_transactions LIMIT 100;"""
                        }
                    }
                }
            }
        }

        # ✅ Create actual folders/files
        self._create_items(base_path, structure)
        print(f"✅ Data Parity structure created at: {os.path.abspath(base_path)}")

    def _create_items(self, path, items):
        """
        Helper function to create directories and files.
        Handles both local and Databricks (DBFS).
        """
        for name, content in items.items():
            new_path = os.path.join(path, name)

            # If running in Databricks, map paths to DBFS
            if self.engine_type == "databricks":
                if new_path.startswith("/Workspace"):
                    raise NotImplementedError("Writing to /Workspace requires Databricks Workspace API.")
                elif not new_path.startswith("/dbfs"):
                    new_path = f"/dbfs{new_path}"

            if isinstance(content, dict):
                if name.endswith(".json"):
                    os.makedirs(path, exist_ok=True)
                    with open(new_path, "w", encoding="utf-8") as f:
                        json.dump(content, f, indent=4)
                else:
                    os.makedirs(new_path, exist_ok=True)
                    self._create_items(new_path, content)

            elif isinstance(content, list):
                with open(new_path, "w", encoding="utf-8") as f:
                    json.dump(content, f, indent=4)

            elif isinstance(content, str):
                os.makedirs(path, exist_ok=True)
                with open(new_path, "w", encoding="utf-8") as f:
                    f.write(content)

            else:
                raise TypeError(f"Unsupported content type {type(content)} for {new_path}")
