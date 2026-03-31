from typing import Any

import dipdup.utils

# Global Patch for DipDup 8.x EVM Parser Bug
# This prevents the indexer from crashing when it encounters arrays (list/Any) in EVM events.
_original_parse_object = dipdup.utils.parse_object


def _fixed_parse_object(type_: Any, data: Any, *args, **kwargs) -> Any:
    # If the type is a primitive or a generic list/Any, bypass the BaseModel check
    if type_ in (list, tuple, Any, any) or str(type_).startswith('list['):
        return data
    return _original_parse_object(type_, data, *args, **kwargs)


dipdup.utils.parse_object = _fixed_parse_object
