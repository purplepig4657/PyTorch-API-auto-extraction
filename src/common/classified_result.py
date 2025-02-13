classified_result = {
    "error": {
        "exist": {
            "class_not_exist": [],
            "function_not_exist": [],
            "parameter_not_exist": [],
        },
        "type": {
            "return_not_matched": [],
            "parameter_not_matched": [],
            "optional_wrong_used": [],
        },
        "value": {
            "not_matched": [],
        },
    },
    "warning": {
        "break_format": {
            "letter_case": [],
            "builtin_type": [],
            "plural": [],
            "unknown_delimiter": [],
            # "unknown_non_type_word": [],
        },
        "type": {
            "doc_undescribed_parameter_type": [],
            "src_undescribed_parameter_type": [],
            "doc_undescribed_return_type": [],
            "src_undescribed_return_type": [],
            # "parameter_not_matched": [],
            # "return_not_matched": [],
            "doc_parameter_generic_type_is_not_specified": [],
            "src_parameter_generic_type_is_not_specified": [],
            "doc_return_generic_type_is_not_specified": [],
            "src_return_generic_type_is_not_specified": [],
        },
        "value": {
            "doc_undescribed_parameter_default": [],
            "src_undescribed_parameter_default": [],
        }
    },
}
