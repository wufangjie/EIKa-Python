import datetime

__all__ = ["config_str", "make_repr"]

config_mysql = {
    "dialect": "mysql",
    "driver": "mysqlconnector",
    "user": "debian-sys-maint",
    "password": "lF66Yxv1DKOh5doW",
    "host": "127.0.0.1",
    "port": 3306,
    "database": "test50"
}


def make_config(config):
    for key in ["driver", "user", "password", "port"]:
        config.setdefault(key, "")
    sep = ["+" if config["driver"] else "",
           ":" if config["password"] else "",
           ":" if config["port"] else ""]
    return "{dialect}{sep[0]}{driver}://{user}{sep[1]}{password}@{host}{sep[2]}{port}/{database}".format(sep=sep, **config)


config_str = make_config(config_mysql)


########################################################################
# make_repr
########################################################################
TYPE_NEED_QUOTE = (
    str,
    datetime.datetime,
    datetime.date,
    datetime.time
)

def make_repr(obj, keys, one_row=True, sep_kv="=", indent="    "):
    """
    keys: the instance's attributes you want to present
    one_row: repr in one row or not (True by default),
             if set True, then ignore `indent` parameter
    """
    if one_row:
        indent = ""
    sep_row = " " if one_row else "\n"
    attr_lst = []
    for key in keys:
        val = getattr(obj, key, None)
        if isinstance(val, TYPE_NEED_QUOTE):
            tmp = '{}{}{}"{}"'
        else:
            tmp = '{}{}{}{}'
        attr_lst.append(tmp.format(indent, key, sep_kv, val))
    attr_str = ("," + sep_row).join(attr_lst)
    return sep_row.join([f"{obj.__class__.__name__} {{", attr_str, "}"])


if __name__ == "__main__":
    print(make_config(config_mysql))
