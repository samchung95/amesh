package provider

type readMode uint8

const (
	readDirect readMode = iota
	readCollection
	readRaw
)

type writeMode uint8

const (
	writeDocument writeMode = iota
	writeSCIMPatch
	writeDocumentField
)

type resourceDescriptor struct {
	Name                  string
	Description           string
	Namespace             bool
	CreateMethod          string
	CreatePath            string
	UpdateMethod          string
	UpdatePath            string
	DeleteMethod          string
	DeletePath            string
	ReadPath              string
	ReadMode              readMode
	ReadCollectionField   string
	ReadMatchField        string
	ReadDocumentField     string
	ServerIDField         string
	RevisionField         string
	Inject                map[string]any
	UpdateMode            writeMode
	UpdateDocumentField   string
	RawDocument           bool
	ReplaceDocument       bool
	RetainOnDelete        bool
	ServerManagedDefaults []string
}

func resourceDescriptors() []resourceDescriptor {
	return []resourceDescriptor{
		{
			Name: "flow", Description: "A versioned AMESH flow document.", Namespace: true,
			CreateMethod: "PUT", CreatePath: "/api/v1/flows",
			UpdateMethod: "PUT", UpdatePath: "/api/v1/flows",
			DeleteMethod: "DELETE", DeletePath: "/api/v1/flows/{namespace}/{key}/revisions/{revision}",
			ReadPath: "/api/v1/flows/{namespace}/{key}/document", ReadDocumentField: "document",
			RevisionField: "revision", RawDocument: true,
			ServerManagedDefaults: []string{"revision", "etag", "semanticHash"},
		},
		{
			Name: "namespace", Description: "An AMESH namespace resource bundle.", Namespace: true,
			CreateMethod: "POST", CreatePath: "/api/v1/namespaces/{namespace}/resource-bundle",
			UpdateMethod: "POST", UpdatePath: "/api/v1/namespaces/{namespace}/resource-bundle",
			ReadPath: "/api/v1/namespaces/{namespace}/resource-bundle", RetainOnDelete: true,
			ServerManagedDefaults: []string{"exportedAt", "checksumSha256"},
		},
		{
			Name: "file", Description: "A versioned file in an AMESH namespace.", Namespace: true,
			CreateMethod: "PUT", CreatePath: "/api/v1/namespaces/{namespace}/files/{key}",
			UpdateMethod: "PUT", UpdatePath: "/api/v1/namespaces/{namespace}/files/{key}",
			DeleteMethod: "DELETE", DeletePath: "/api/v1/namespaces/{namespace}/files/{key}",
			ReadPath: "/api/v1/namespaces/{namespace}/files/{key}", ReadMode: readRaw, RawDocument: true,
			RevisionField: "resourceVersion",
		},
		{
			Name: "key_value", Description: "A typed key-value entry in an AMESH namespace.", Namespace: true,
			CreateMethod: "PUT", CreatePath: "/api/v1/namespaces/{namespace}/key-values/{key}",
			UpdateMethod: "PUT", UpdatePath: "/api/v1/namespaces/{namespace}/key-values/{key}",
			DeleteMethod: "DELETE", DeletePath: "/api/v1/namespaces/{namespace}/key-values/{key}",
			ReadPath: "/api/v1/namespaces/{namespace}/key-values/{key}", RevisionField: "resourceVersion",
			ServerManagedDefaults: []string{"namespace", "key", "resourceVersion", "createdAt", "updatedAt"},
		},
		{
			Name: "dashboard", Description: "An AMESH dashboard definition.",
			CreateMethod: "PUT", CreatePath: "/api/v1/dashboards/{key}",
			UpdateMethod: "PUT", UpdatePath: "/api/v1/dashboards/{key}",
			DeleteMethod: "DELETE", DeletePath: "/api/v1/dashboards/{key}",
			ReadPath: "/api/v1/dashboards/{key}", RevisionField: "version",
			ServerManagedDefaults: []string{"id", "version", "createdAt", "updatedAt"},
		},
		{
			Name: "app", Description: "An AMESH workflow application.", Namespace: true,
			CreateMethod: "PUT", CreatePath: "/api/v1/apps/{namespace}/{key}",
			UpdateMethod: "PUT", UpdatePath: "/api/v1/apps/{namespace}/{key}",
			ReadPath: "/api/v1/apps/{namespace}/{key}", RetainOnDelete: true, RevisionField: "revision",
			ServerManagedDefaults: []string{"namespace", "id", "revision", "createdAt", "updatedAt"},
		},
		{
			Name: "user", Description: "A SCIM user managed through AMESH.",
			CreateMethod: "POST", CreatePath: "/scim/v2/Users",
			UpdateMethod: "PATCH", UpdatePath: "/scim/v2/Users/{server_id}", UpdateMode: writeSCIMPatch,
			DeleteMethod: "DELETE", DeletePath: "/scim/v2/Users/{server_id}",
			ReadPath: "/scim/v2/Users/{server_id}", ServerIDField: "id",
			ServerManagedDefaults: []string{"id", "meta"},
		},
		{
			Name: "group", Description: "A SCIM group managed through AMESH.",
			CreateMethod: "POST", CreatePath: "/scim/v2/Groups",
			UpdateMethod: "PATCH", UpdatePath: "/scim/v2/Groups/{server_id}", UpdateMode: writeSCIMPatch,
			DeleteMethod: "DELETE", DeletePath: "/scim/v2/Groups/{server_id}",
			ReadPath: "/scim/v2/Groups/{server_id}", ServerIDField: "id",
			ServerManagedDefaults: []string{"id", "meta"},
		},
		{
			Name: "role", Description: "An AMESH authorization role.",
			CreateMethod: "PUT", CreatePath: "/api/v1/admin/roles/{key}",
			UpdateMethod: "PUT", UpdatePath: "/api/v1/admin/roles/{key}",
			ReadPath: "/api/v1/admin/roles", ReadMode: readCollection, ReadMatchField: "name",
			RetainOnDelete: true, ServerManagedDefaults: []string{"built_in"},
		},
		{
			Name: "binding", Description: "An immutable AMESH role binding.",
			CreateMethod: "POST", CreatePath: "/api/v1/admin/bindings",
			DeleteMethod: "DELETE", DeletePath: "/api/v1/admin/bindings/{server_id}",
			ReadPath: "/api/v1/admin/bindings", ReadMode: readCollection, ReadMatchField: "id",
			ServerIDField: "id", ReplaceDocument: true,
		},
		{
			Name: "service_account", Description: "An immutable AMESH service-account principal.",
			CreateMethod: "POST", CreatePath: "/api/v1/admin/principals",
			ReadPath: "/api/v1/admin/principals", ReadMode: readCollection, ReadMatchField: "id",
			ServerIDField: "id", Inject: map[string]any{"principal_type": "SERVICE_ACCOUNT"},
			ReplaceDocument: true, RetainOnDelete: true, ServerManagedDefaults: []string{"id", "metadata"},
		},
		{
			Name: "tenant", Description: "An AMESH tenant and its policy.",
			CreateMethod: "POST", CreatePath: "/api/v1/admin/tenants",
			UpdateMethod: "PUT", UpdatePath: "/api/v1/admin/tenants/{key}/policy",
			UpdateMode: writeDocumentField, UpdateDocumentField: "policy",
			DeleteMethod: "DELETE", DeletePath: "/api/v1/admin/tenants/{key}",
			ReadPath: "/api/v1/admin/tenants/{key}", ServerIDField: "id",
			ServerManagedDefaults: []string{"id", "metadata", "status", "storage_prefix"},
		},
		{
			Name: "worker_group", Description: "The worker-group policy set for an AMESH tenant.", Namespace: true,
			CreateMethod: "PUT", CreatePath: "/api/v1/admin/tenants/{namespace}/policy",
			UpdateMethod: "PUT", UpdatePath: "/api/v1/admin/tenants/{namespace}/policy",
			ReadPath: "/api/v1/admin/tenants/{namespace}", ReadDocumentField: "policy",
			RetainOnDelete: true,
		},
		{
			Name: "plugin_policy", Description: "An AMESH plugin policy rule.", Namespace: true,
			CreateMethod: "POST", CreatePath: "/api/v1/plugin-policy/rules",
			UpdateMethod: "PUT", UpdatePath: "/api/v1/plugin-policy/rules/{server_id}",
			DeleteMethod: "DELETE", DeletePath: "/api/v1/plugin-policy/rules/{server_id}",
			ReadPath: "/api/v1/plugin-policy/rules/{server_id}", ServerIDField: "id",
			ServerManagedDefaults: []string{"id", "tenantId", "createdAt", "createdBy", "updatedAt", "updatedBy"},
		},
	}
}
