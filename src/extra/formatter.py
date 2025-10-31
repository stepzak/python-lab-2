from src.cmd_types.formats import ErrFormat


def formatter(exc, form: ErrFormat) -> str:
    str_format = form.format_str
    attrs = form.attrs
    if attrs:
        formats = []
        for attr in attrs:
            spliited = attr.attr_name.split(".")
            cur_attr = getattr(exc, spliited[0])
            for spl in spliited[1:]:
                cur_attr = getattr(cur_attr, spl)

            for getter in attr.attr_getters:
                cur_attr = cur_attr.__getitem__[getter]

            formats.append(cur_attr)

        str_format = str_format.format(*formats)
    return str_format
