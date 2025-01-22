import re

def cql_filter_string_to_qgis_filter_string(cql_filter_string, params):

    cql_filter_string = re.sub("%","%25",cql_filter_string)
    parts = re.split(r"(\"[^\"]*\"|\'[^\']*\'|\(|\)|!=|<=|>=|<|>|=|IS NOT|IS|LIKE|ILIKE|AND|OR|NOT|NULL|IN|,|(?<==|<|>|\()\d+\.*\d*|\[|\]|BETWEEN)", cql_filter_string)


    parts = [blankspace.strip() for blankspace in parts if blankspace.strip()]

    qgis_filter_string = f"{params['LAYERS']}:"
    for i, part in enumerate(parts):
        if bool(re.match(r"(\"[^\"]*\"|\'[^\']*\'|\(|\)|!=|<=|>=|<|>|=|IS NOT|IS|LIKE|AND|OR|NOT|NULL|\d+\.*\d*|,)", part)) == True:
            qgis_filter_string += part + " "
        elif part == "[":
            qgis_filter_string += "( "
        elif part == "]":
            qgis_filter_string += ") "
        elif part == "ILIKE":
            qgis_filter_string += "LIKE "
        elif part == "BETWEEN":
            qgis_filter_string += f"> {parts[i+1]} AND \"{parts[i-1]}\" < {parts[i+3]} "
            parts[i+1] = ""
            parts[i+2] = ""
            parts[i+3] = ""
        elif part == "IN":
            j = 0
            print(parts[i+2+j*2])
            while bool(re.match(r"\'.*\.\d+\'", parts[i+2+j*2])):
                if parts[i+3+j*2] == ")":
                    j += 1
                    break
                j += 1
            if j > 0:
                qgis_filter_string += "\"id\" IN "
                for k in range (j):
                    layer_dot_id = parts[i+2+k*2]
                    id = re.sub(r".*\.+","",layer_dot_id)
                    id_no_parenthesis = re.sub(r"\'","",id)
                    qgis_filter_string += parts[i+1+k*2] + " " + id_no_parenthesis + " "
                    parts[i+1+k*2] = ""
                    parts[i+2+k*2] = ""

            else:
                qgis_filter_string += part + " "


        elif part == "":
            pass
        else:
            qgis_filter_string += "\"" + part + "\" "

    return qgis_filter_string