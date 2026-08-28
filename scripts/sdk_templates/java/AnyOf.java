package io.amesh.client.model;

import com.fasterxml.jackson.annotation.JsonCreator;
import com.fasterxml.jackson.annotation.JsonValue;
import io.amesh.client.ApiClient;

/** Arbitrary JSON value used when OpenAPI intentionally leaves a field unconstrained. */
public final class AnyOf {
    private final Object value;

    @JsonCreator(mode = JsonCreator.Mode.DELEGATING)
    public AnyOf(Object value) {
        this.value = value;
    }

    @JsonValue
    public Object getValue() {
        return value;
    }

    public String toUrlQueryString(String prefix) {
        String key = prefix == null ? "" : prefix;
        return String.format(
                java.util.Locale.ROOT,
                "%s=%s",
                key,
                ApiClient.urlEncode(ApiClient.valueToString(value)));
    }
}
