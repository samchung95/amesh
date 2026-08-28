package ameshclient

import "encoding/json"

// AnyOf is an unconstrained JSON value from the OpenAPI contract.
type AnyOf = any

// NullableAnyOf distinguishes missing, explicit null and arbitrary JSON values.
type NullableAnyOf struct {
	value *AnyOf
	isSet bool
}

func (v NullableAnyOf) Get() *AnyOf { return v.value }

func (v *NullableAnyOf) Set(value *AnyOf) {
	v.value = value
	v.isSet = true
}

func (v NullableAnyOf) IsSet() bool { return v.isSet }

func (v *NullableAnyOf) Unset() {
	v.value = nil
	v.isSet = false
}

func NewNullableAnyOf(value *AnyOf) *NullableAnyOf {
	return &NullableAnyOf{value: value, isSet: true}
}

func (v NullableAnyOf) MarshalJSON() ([]byte, error) { return json.Marshal(v.value) }

func (v *NullableAnyOf) UnmarshalJSON(source []byte) error {
	v.isSet = true
	return json.Unmarshal(source, &v.value)
}
