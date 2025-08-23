(class_declaration
  name: (identifier) @name.definition.class) @definition.class

(method_declaration
  name: (identifier) @name.definition.method) @definition.method

; Methods can also be considered functions for consistency
(method_declaration
  name: (identifier) @name.definition.function) @definition.function

(method_invocation
  name: (identifier) @name.reference.method
  arguments: (argument_list) @reference.call)

(interface_declaration
  name: (identifier) @name.definition.interface) @definition.interface

(type_list
  (type_identifier) @name.reference.interface) @reference.implementation

(object_creation_expression
  type: (type_identifier) @name.reference.class) @reference.class

(superclass (type_identifier) @name.reference.class) @reference.class

(import_declaration
  (scoped_identifier) @name.import) @import

(import_declaration
  (identifier) @name.import) @import

(package_declaration
  (scoped_identifier) @name.definition.module) @definition.module