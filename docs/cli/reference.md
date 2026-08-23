# AMESH CLI command reference

Generated from `build_parser()`.

## `amesh`

```text
usage: amesh [-h] [--version] [--api-url API_URL] [--token TOKEN]
             [--tenant TENANT] [--profile PROFILE] [--config-path CONFIG_PATH]
             [--output {human,json,quiet}] [--quiet]
             {validate,apply,flows,executions,run,execution,logs,webhook,plugins,namespace,auth,config,flow,admin,lifecycle,upgrade,kestra,completion,command-docs,storage,recovery,tenant-transfer} ...
```

## `amesh admin`

```text
usage: amesh admin [-h] {configuration,tenants} ...
```

## `amesh admin configuration`

```text
usage: amesh admin configuration [-h] {show,diagnostics,reload} ...
```

## `amesh admin configuration diagnostics`

```text
usage: amesh admin configuration diagnostics [-h]
```

## `amesh admin configuration reload`

```text
usage: amesh admin configuration reload [-h]
```

## `amesh admin configuration show`

```text
usage: amesh admin configuration show [-h]
```

## `amesh admin tenants`

```text
usage: amesh admin tenants [-h]
                           {list,get,create,suspend,restore,export,delete} ...
```

## `amesh admin tenants create`

```text
usage: amesh admin tenants create [-h] --display-name DISPLAY_NAME slug
```

## `amesh admin tenants delete`

```text
usage: amesh admin tenants delete [-h] [--force] slug
```

## `amesh admin tenants export`

```text
usage: amesh admin tenants export [-h] slug
```

## `amesh admin tenants get`

```text
usage: amesh admin tenants get [-h] slug
```

## `amesh admin tenants list`

```text
usage: amesh admin tenants list [-h]
```

## `amesh admin tenants restore`

```text
usage: amesh admin tenants restore [-h] slug
```

## `amesh admin tenants suspend`

```text
usage: amesh admin tenants suspend [-h] slug
```

## `amesh apply`

```text
usage: amesh apply [-h] path
```

## `amesh auth`

```text
usage: amesh auth [-h] {bootstrap-admin,token} ...
```

## `amesh auth bootstrap-admin`

```text
usage: amesh auth bootstrap-admin [-h] --handle HANDLE
                                  --display-name DISPLAY_NAME
                                  [--password-stdin]
```

## `amesh auth token`

```text
usage: amesh auth token [-h] {store,status,delete} ...
```

## `amesh auth token delete`

```text
usage: amesh auth token delete [-h]
```

## `amesh auth token status`

```text
usage: amesh auth token status [-h]
```

## `amesh auth token store`

```text
usage: amesh auth token store [-h] [--stdin]
```

## `amesh command-docs`

```text
usage: amesh command-docs [-h] [path]
```

## `amesh completion`

```text
usage: amesh completion [-h] {bash,zsh,fish,powershell}
```

## `amesh config`

```text
usage: amesh config [-h] {show,set,use,profiles} ...
```

## `amesh config profiles`

```text
usage: amesh config profiles [-h]
```

## `amesh config set`

```text
usage: amesh config set [-h] [--api-url PROFILE_API_URL]
                        [--tenant PROFILE_TENANT]
                        name
```

## `amesh config show`

```text
usage: amesh config show [-h]
```

## `amesh config use`

```text
usage: amesh config use [-h] name
```

## `amesh execution`

```text
usage: amesh execution [-h] execution_id
```

## `amesh executions`

```text
usage: amesh executions [-h] [--limit LIMIT]
```

## `amesh flow`

```text
usage: amesh flow [-h] {apply,diff,export,delete,test} ...
```

## `amesh flow apply`

```text
usage: amesh flow apply [-h] [path]
```

## `amesh flow delete`

```text
usage: amesh flow delete [-h] [--force] namespace flow_id revision
```

## `amesh flow diff`

```text
usage: amesh flow diff [-h] [path]
```

## `amesh flow export`

```text
usage: amesh flow export [-h] [--revision REVISION] namespace flow_id [path]
```

## `amesh flow test`

```text
usage: amesh flow test [-h] --revision REVISION [--test-id TEST_ID]
                       [--fail-fast]
                       namespace flow_id
```

## `amesh flows`

```text
usage: amesh flows [-h]
```

## `amesh kestra`

```text
usage: amesh kestra [-h] {flow,migration,compatibility} ...
```

## `amesh kestra compatibility`

```text
usage: amesh kestra compatibility [-h] {manifest} ...
```

## `amesh kestra compatibility manifest`

```text
usage: amesh kestra compatibility manifest [-h]
```

## `amesh kestra flow`

```text
usage: amesh kestra flow [-h] {validate,migrate} ...
```

## `amesh kestra flow migrate`

```text
usage: amesh kestra flow migrate [-h] --output-path OUTPUT_PATH path
```

## `amesh kestra flow validate`

```text
usage: amesh kestra flow validate [-h] path
```

## `amesh kestra migration`

```text
usage: amesh kestra migration [-h] {plan,import} ...
```

## `amesh kestra migration import`

```text
usage: amesh kestra migration import [-h] --target-dir TARGET_DIR
                                     [--max-records MAX_RECORDS]
                                     [--secret-binding SECRET_BINDING]
                                     bundle
```

## `amesh kestra migration plan`

```text
usage: amesh kestra migration plan [-h] [--secret-binding SECRET_BINDING]
                                   bundle
```

## `amesh lifecycle`

```text
usage: amesh lifecycle [-h]
                       {policies,create-policy,preview,jobs,execute,resume,holds,hold,release-hold} ...
```

## `amesh lifecycle create-policy`

```text
usage: amesh lifecycle create-policy [-h]
                                     --resource-type {EXECUTION,LOG,METRIC,ARTIFACT,CACHE}
                                     --scope {INSTANCE,TENANT,NAMESPACE,LABEL}
                                     [--namespace NAMESPACE] [--label LABEL]
                                     --retention-days RETENTION_DAYS
                                     [--batch-size BATCH_SIZE]
                                     [--schedule-minutes SCHEDULE_MINUTES]
                                     --reason REASON
```

## `amesh lifecycle execute`

```text
usage: amesh lifecycle execute [-h] [--force] job_id
```

## `amesh lifecycle hold`

```text
usage: amesh lifecycle hold [-h] --reason REASON
                            [--resource-type {EXECUTION,LOG,METRIC,ARTIFACT,CACHE}]
                            [--resource-id RESOURCE_ID]
                            [--namespace NAMESPACE] [--label LABEL]
                            [--data-from DATA_FROM] [--data-to DATA_TO]
                            name
```

## `amesh lifecycle holds`

```text
usage: amesh lifecycle holds [-h]
```

## `amesh lifecycle jobs`

```text
usage: amesh lifecycle jobs [-h]
```

## `amesh lifecycle policies`

```text
usage: amesh lifecycle policies [-h]
```

## `amesh lifecycle preview`

```text
usage: amesh lifecycle preview [-h] --reason REASON policy_id
```

## `amesh lifecycle release-hold`

```text
usage: amesh lifecycle release-hold [-h] hold_id
```

## `amesh lifecycle resume`

```text
usage: amesh lifecycle resume [-h] job_id
```

## `amesh logs`

```text
usage: amesh logs [-h] execution_id
```

## `amesh namespace`

```text
usage: amesh namespace [-h] {files,kv,secrets,resources} ...
```

## `amesh namespace files`

```text
usage: amesh namespace files [-h]
                             {list,upload,download,move,versions,delete} ...
```

## `amesh namespace files delete`

```text
usage: amesh namespace files delete [-h] [--expected-version EXPECTED_VERSION]
                                    namespace remote_path
```

## `amesh namespace files download`

```text
usage: amesh namespace files download [-h] [--version VERSION]
                                      namespace remote_path local_path
```

## `amesh namespace files list`

```text
usage: amesh namespace files list [-h] [--local-only] namespace
```

## `amesh namespace files move`

```text
usage: amesh namespace files move [-h] [--expected-version EXPECTED_VERSION]
                                  namespace remote_path destination_path
```

## `amesh namespace files upload`

```text
usage: amesh namespace files upload [-h] [--content-type CONTENT_TYPE]
                                    [--expected-version EXPECTED_VERSION]
                                    namespace remote_path local_path
```

## `amesh namespace files versions`

```text
usage: amesh namespace files versions [-h] namespace remote_path
```

## `amesh namespace kv`

```text
usage: amesh namespace kv [-h] {list,get,set,delete,changes} ...
```

## `amesh namespace kv changes`

```text
usage: amesh namespace kv changes [-h] [--after AFTER] [--limit LIMIT]
                                  namespace
```

## `amesh namespace kv delete`

```text
usage: amesh namespace kv delete [-h] [--expected-version EXPECTED_VERSION]
                                 namespace key
```

## `amesh namespace kv get`

```text
usage: amesh namespace kv get [-h] namespace key
```

## `amesh namespace kv list`

```text
usage: amesh namespace kv list [-h] namespace
```

## `amesh namespace kv set`

```text
usage: amesh namespace kv set [-h]
                              --type {STRING,NUMBER,BOOLEAN,DATETIME,DATE,DURATION,JSON}
                              --value VALUE [--expires-at EXPIRES_AT]
                              [--expected-version EXPECTED_VERSION]
                              namespace key
```

## `amesh namespace resources`

```text
usage: amesh namespace resources [-h] {export,import} ...
```

## `amesh namespace resources export`

```text
usage: amesh namespace resources export [-h] namespace path
```

## `amesh namespace resources import`

```text
usage: amesh namespace resources import [-h] namespace path
```

## `amesh namespace secrets`

```text
usage: amesh namespace secrets [-h] {list,bind,delete} ...
```

## `amesh namespace secrets bind`

```text
usage: amesh namespace secrets bind [-h] [--expected-version EXPECTED_VERSION]
                                    namespace key environment_name
```

## `amesh namespace secrets delete`

```text
usage: amesh namespace secrets delete [-h]
                                      [--expected-version EXPECTED_VERSION]
                                      namespace key
```

## `amesh namespace secrets list`

```text
usage: amesh namespace secrets list [-h] [--local-only] namespace
```

## `amesh plugins`

```text
usage: amesh plugins [-h]
                     {list,refresh,install,scaffold,certify,docs,sandbox,criteria} ...
```

## `amesh plugins certify`

```text
usage: amesh plugins certify [-h] [--platform-version PLATFORM_VERSION]
                             [--output OUTPUT]
                             path
```

## `amesh plugins criteria`

```text
usage: amesh plugins criteria [-h]
```

## `amesh plugins docs`

```text
usage: amesh plugins docs [-h] --output-dir OUTPUT_DIR path
```

## `amesh plugins install`

```text
usage: amesh plugins install [-h] --sha256 SHA256 path
```

## `amesh plugins list`

```text
usage: amesh plugins list [-h]
```

## `amesh plugins refresh`

```text
usage: amesh plugins refresh [-h]
```

## `amesh plugins sandbox`

```text
usage: amesh plugins sandbox [-h] --configuration CONFIGURATION
                             path entry_point
```

## `amesh plugins scaffold`

```text
usage: amesh plugins scaffold [-h] --name NAME path
```

## `amesh recovery`

```text
usage: amesh recovery [-h] {create,verify-latest,exercise} ...
```

## `amesh recovery create`

```text
usage: amesh recovery create [-h] [--actor ACTOR]
```

## `amesh recovery exercise`

```text
usage: amesh recovery exercise [-h] [--actor ACTOR] [--profile PROFILE]
                               [--scheduled]
```

## `amesh recovery verify-latest`

```text
usage: amesh recovery verify-latest [-h] [--actor ACTOR] [--profile PROFILE]
                                    [--scheduled]
```

## `amesh run`

```text
usage: amesh run [-h] [--runner {local,kubernetes}] [--input INPUT]
                 [--idempotency-key IDEMPOTENCY_KEY]
                 namespace flow_id
```

## `amesh storage`

```text
usage: amesh storage [-h] {validate,migrate} ...
```

## `amesh storage migrate`

```text
usage: amesh storage migrate [-h] --checkpoint CHECKPOINT destination_config
```

## `amesh storage validate`

```text
usage: amesh storage validate [-h] [--metadata-only]
```

## `amesh tenant-transfer`

```text
usage: amesh tenant-transfer [-h] {export,import} ...
```

## `amesh tenant-transfer export`

```text
usage: amesh tenant-transfer export [-h] [--actor ACTOR] tenant_slug path
```

## `amesh tenant-transfer import`

```text
usage: amesh tenant-transfer import [-h] [--actor ACTOR] path target_slug
```

## `amesh upgrade`

```text
usage: amesh upgrade [-h]
                     {policy,preflight,postflight,events-preview,events-upcast,migrate-config} ...
```

## `amesh upgrade events-preview`

```text
usage: amesh upgrade events-preview [-h]
```

## `amesh upgrade events-upcast`

```text
usage: amesh upgrade events-upcast [-h] --reason REASON
                                   [--batch-size BATCH_SIZE] [--force]
```

## `amesh upgrade migrate-config`

```text
usage: amesh upgrade migrate-config [-h] --target-version TARGET_VERSION
                                    --output OUTPUT
                                    {flow,plugin} path
```

## `amesh upgrade policy`

```text
usage: amesh upgrade policy [-h]
```

## `amesh upgrade postflight`

```text
usage: amesh upgrade postflight [-h] --from-version FROM_VERSION
                                --to-version TO_VERSION
```

## `amesh upgrade preflight`

```text
usage: amesh upgrade preflight [-h] --from-version FROM_VERSION
                               --to-version TO_VERSION
```

## `amesh validate`

```text
usage: amesh validate [-h] [--json] path
```

## `amesh webhook`

```text
usage: amesh webhook [-h] [--runner {local,kubernetes}] [--input INPUT]
                     namespace flow_id trigger_id
```
