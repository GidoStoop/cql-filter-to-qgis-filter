import re
from qgis.core import QgsMessageLog

def negation_at_start(cql_filter_string):
    cql_filter_string = cql_filter_string.strip()
    if bool(re.match(r"NOT", cql_filter_string, re.I)):
        return "NOT "
    else:
        return ""

def in_parentheses(string):
    string = string.strip()
    if string.startswith("(") and string.endswith(")"):
        return ["(",")"]
    else:
        return ["",""]

def cql_to_qgis_conditional_expressions(conditional_expressions_list):
    comparison_operator = ['=', '<', '>', '>=', '<=', '!=', 'IS', 'IS NOT', 'LIKE','ILIKE'] # Make case insensitive
    qgis_conditional_expression_list = []
    for conditional_expression in conditional_expressions_list:
        if any(i in conditional_expression for i in comparison_operator): #Isn't this always the case?

            #Check field for negation
            negation_at_start_before_parenthesis = negation_at_start(conditional_expression)
            conditional_expression = re.sub(r'^\s*NOT','',conditional_expression,flags=re.I) 

            #Check field for enclosure in parenthesese
            conditional_expression_in_parentheses = in_parentheses(conditional_expression)
            conditional_expression = re.sub(r'^\s*\(','',conditional_expression)
            conditional_expression = re.sub(r'\)\s*$','',conditional_expression)

            #Check field for negation again
            negation_at_start_after_parenthesis = negation_at_start(conditional_expression)
            conditional_expression = re.sub(r'^\s*NOT','',conditional_expression,flags=re.I)

            field_value = re.split(r"=|<|>|<=|>=|!=|IS|IS NOT|LIKE|ILIKE", conditional_expression) #how does it work with NULL value in qgisserver?, What if any of these is inside the value or field name
            field, value = field_value[0], field_value[1]
            operator = conditional_expression.strip(field).strip(value)

            #In QGIS server, Like is already case insensitive
            if operator == "ILIKE":
                operator = "LIKE"

            QgsMessageLog.logMessage(value)

            field = field.strip()
            value = value.strip()

            #If the value has multiple entries like: ('Entry One', 'Entry Two', 'Entry Three'), add whitespaces
            if re.match(r"^\(\s*'.*',\s*'.*'", value):
                pass # To do: Fix

            #Construct new string
            qgis_conditional_expression_string = negation_at_start_before_parenthesis
            qgis_conditional_expression_string += conditional_expression_in_parentheses[0]
            qgis_conditional_expression_string += negation_at_start_after_parenthesis
            qgis_conditional_expression_string += f"\"{field}\" "
            qgis_conditional_expression_string += operator
            qgis_conditional_expression_string += f" {value}"
            qgis_conditional_expression_string += conditional_expression_in_parentheses[1]

            qgis_conditional_expression_list.append(qgis_conditional_expression_string)

            QgsMessageLog.logMessage(qgis_conditional_expression_string)
        return qgis_conditional_expression_list

def cql_filter_string_to_qgis_filter_string(cql_filter_string, params):

    #Check if full function is in parenthesis
    cql_filter_in_parentheses = in_parentheses(cql_filter_string)
    cql_filter_string = re.sub(r'^\s*\(','',cql_filter_string)
    cql_filter_string = re.sub(r'$\)\s*','',cql_filter_string)

    binary_logic_operator = ['AND', 'OR']

    #If binary operator in query, split the query
    if any(i in cql_filter_string for i in binary_logic_operator):

        binary_logic_operators_list = [operator for operator in binary_logic_operator if operator in cql_filter_string]
        conditional_expressions_list = re.split(r"AND|OR", cql_filter_string)

    #Else, continue with list with just one entry
    else: 
        conditional_expressions_list = [cql_filter_string]

    qgis_conditional_expression_list = cql_to_qgis_conditional_expressions(conditional_expressions_list)

    #init filter string with possible negation
    qgis_filter_string = ""
    for i in range(len(qgis_conditional_expression_list)):
        qgis_filter_string += qgis_conditional_expression_list[i]
        if i+1 < len(qgis_conditional_expression_list):
            qgis_filter_string += " "
            qgis_filter_string += binary_logic_operators_list[i]
            qgis_filter_string += " "
            
    #request.setParameter('SERVICE', 'CUSTOM')
    qgis_filter_string = f"{params['LAYERS']}:{cql_filter_in_parentheses[0]} {qgis_filter_string} {cql_filter_in_parentheses[1]}"

    return qgis_filter_string