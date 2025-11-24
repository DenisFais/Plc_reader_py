from __future__ import annotations

from pyparsing import *
from data_type import standard_types_

# ----------------------------------------------------------------------
# Primitives
# ----------------------------------------------------------------------
elememnt_name = Word(alphanums + ".-_/") | QuotedString('"')
element_type = Word(alphas + '"')
element_value = Suppress(Group(Literal(":") + Word(nums + ".")))
value = Word(alphanums + '."[]')
element_attribute = Optional(Suppress("{" + SkipTo("}") + "}"))
spacer = Suppress(":")
std_element = oneOf(list(standard_types_))
udt_type_name = QuotedString('"')  # solo nome tipo UDT
number = Word(nums)
comment = Suppress("//" + rest_of_line)
value_assignment = Suppress(":=") + SkipTo(";")("start_value")
end_of_line = Optional(value_assignment) + Suppress(";" + restOfLine)
element_header = elememnt_name("name") + element_attribute + spacer


arr_size = Group(
    Suppress("Array[")
    + number("start_array")
    + Suppress("..")
    + number("end_array")
    + Suppress("] of")
)

# ----------------------------------------------------------------------
# TYPE STANDARD
# ----------------------------------------------------------------------
std_type = Group(
    elememnt_name("name")
    + element_attribute
    + spacer
    + std_element("type")
    + end_of_line
    + Optional(Suppress(Literal(":") + Word(nums + ".")))
)

# ----------------------------------------------------------------------
# TYPE UDT (campo che usa un UDT come tipo)
# ----------------------------------------------------------------------
udt_field = Group(
    elememnt_name("name")
    + element_attribute
    + spacer
    + udt_type_name("type")
    + end_of_line
)

# ----------------------------------------------------------------------
# TYPE ARRAY
# ----------------------------------------------------------------------
array_type = Group(
    elememnt_name("name")
    + element_attribute
    + spacer
    + arr_size("array_length")
    + (udt_type_name | std_element)("type")
    + end_of_line
)

# ----------------------------------------------------------------------
# TYPE STRUCT (campo struct annidato)
# ----------------------------------------------------------------------
struct_type_forward = Forward()

# QUI: tolto Suppress(LineEnd()) che ti rompeva la 3a UDT
struct_type = Group(
    elememnt_name("name")
    + element_attribute
    + spacer
    + Literal("Struct")("type")
    + Optional(comment)
    + OneOrMore(
        std_type
        | udt_field
        | array_type
        | struct_type_forward
    )("element")
    + Suppress("END_STRUCT;")
)

struct_type_forward <<= struct_type

# ----------------------------------------------------------------------
# TYPE UDT (definizione di UDT completo)
# ----------------------------------------------------------------------
udt_header = (
    Suppress("TYPE")
    + QuotedString('"')("udt_name")
    + Optional(element_attribute)
    + Suppress("VERSION")
    + Suppress(":")
    + Suppress(Word(nums + "."))
    + Suppress("STRUCT")
)

udt_footer = (
    Suppress("END_STRUCT;")
    + Optional(Empty())
    + Suppress("END_TYPE")
    + Optional(Suppress(";"))  # per sicurezza, se mai ci fosse il ';'
)

udt_forward = Forward()

udt_struct = (
    udt_header
    + OneOrMore(
        std_type
        | udt_field
        | array_type
        | struct_type
        | udt_forward
    )("udt")
    + udt_footer
)

udt_forward <<= udt_struct

# ----------------------------------------------------------------------
# TYPE DB (due varianti: con STRUCT, o legato direttamente a UDT)
# ----------------------------------------------------------------------
db_header = (
    Suppress("DATA_BLOCK")
    + QuotedString('"')("db_name")
    + element_attribute
    + Suppress("VERSION")
    + Suppress(":")
    + Suppress(Word(nums + "."))
)

# Variante 1: DB con STRUCT ... END_STRUCT;
db_body_struct = (
    Suppress("STRUCT")
    + OneOrMore(std_type | array_type | udt_field | struct_type)("db_elements")
    + Suppress("END_STRUCT;")
    + Suppress("END_DATA_BLOCK")
)

# Variante 2: DB che punta a una UDT ("RicettaFifoUDT")
db_body_udt = (
    udt_type_name("db_udt_type")
    + Suppress("END_DATA_BLOCK")
)

db_struct = Group(
    db_header
    + (db_body_struct | db_body_udt)
)("struct_field")

# ----------------------------------------------------------------------
# MAP DECLARATION: N UDT + 1 DB
# ----------------------------------------------------------------------
map_struct = (
    OneOrMore(Group(udt_struct))("udt_field")
    + db_struct
    + StringEnd()
)

