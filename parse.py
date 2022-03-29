import javalang
import re
import os
import sys


NAME = 'name'
DOCUMENTATION = 'documentation'
ENCLOSING_CLASSES = 'enclosing_classes'
INPUT_PARAMETERS = 'input_parameters'
RETURN_TYPE = 'return_type'
BODY = 'body'


def gather_source_file_paths(dataset_dir_path):
    """Gathers a list of paths to all source files in a dataset directory.

    Args:
        dataset_dir_path: Path to root directory of dataset

    Returns:
        List of paths to all source files as strings
    """
    dataset_dir_normpath = os.path.normpath(dataset_dir_path)
    source_file_paths = []

    for dir_path, _, file_names in os.walk(dataset_dir_normpath):
        for file_name in file_names:
            source_file_path = os.path.join(dir_path, file_name)
            source_file_paths.append(source_file_path)

    return source_file_paths


def parse_and_write_source_files(
        source_file_paths, output_file_path, verbose=True, process_id=0):
    """Parses a list of source files and writes them to a text file.

    Args:
        source_file_paths: List of source file paths
        output_file_path: Path to the output file
        verbose: Whether to print update messages to the console
    """
    n_files = len(source_file_paths)
    n_methods = 0

    with open(output_file_path, 'w') as output_file:

        for i, source_file_path in enumerate(source_file_paths):
            methods = parse_source_file(source_file_path)

            for method in methods:
                output_file.write(method[NAME])
                output_file.write('\n')
                output_file.write(method[DOCUMENTATION])
                output_file.write('\n')
                output_file.write(method[ENCLOSING_CLASSES])
                output_file.write('\n')
                output_file.write(method[INPUT_PARAMETERS])
                output_file.write('\n')
                output_file.write(method[RETURN_TYPE])
                output_file.write('\n')
                output_file.write(method[BODY])
                output_file.write('\n')

            n_methods += len(methods)

            if verbose and (i + 1) % 1000 == 0:
                print(
                    f'Process {process_id}:',
                    f'Completed {i + 1} / {n_files} files',
                    f'(~{(i + 1) / n_files * 100:.1f}%),',
                    f'{n_methods} methods processed')

    print(
        f'Process {process_id}: Completed {n_files} files,',
        f'{n_methods} methods processed')


def parse_source_file(source_file_path):
    """Parses a .java source file, extracting relevant contexts.

    The relevant contexts for each method include the method name,
    documentation (Javadoc), enclosing classes, input parameters (names and
    types), return type, and body names. Each method will be represented as a
    dictionary containing all of these contexts.

    Methods without Javadoc documentation are ignored.

    Args:
        source_file_path: String path to the .java source file

    Returns:
        List of dictionaries, each containing the contexts for each method
    """
    methods = []

    tree = build_parse_tree(source_file_path)

    if not tree:
        return methods

    sys.setrecursionlimit(10000)

    for path, node in tree.filter(javalang.tree.MethodDeclaration):
        name = ' '.join(convert_name_to_tokens(node.name))
        documentation = get_documentation(node)

        if documentation:
            body = get_body(node)

            if body:
                enclosing_classes = get_enclosing_classes(path)
                input_parameters = get_input_parameters(node)
                return_type = get_return_type(node)

                method = {
                    NAME: name,
                    DOCUMENTATION: documentation,
                    ENCLOSING_CLASSES: enclosing_classes,
                    INPUT_PARAMETERS: input_parameters,
                    RETURN_TYPE: return_type,
                    BODY: body,
                }
                methods.append(method)

    return methods


def build_parse_tree(source_file_path):
    """Builds the javalang parse tree from a path to a Java source file.

    Args:
        source_file_path: String path to Java source file

    Returns:
        javalang tree object for the source file, or None if syntax error
    """
    try:
        with open(source_file_path, encoding='utf-8') as source_file:
            source = source_file.read()
        return javalang.parse.parse(source)
    except:
        return None


def get_body(method_declaration):
    """Gets the set of method body names from a MethodDeclaration node.

    There are several types of nodes that include relevant method body names,
    two of which are MemberReference and MethodInvocation. We should attempt to
    include all possible node types. Applying filters individually causes us to
    append the names out of order, which may cause adverse results.

    Method body names are gathered into a set (no duplicates, no ordering).

    The current node types included are:
        - MemberReference
        - MethodInvocation
        - SuperMethodInvocation
        - SuperMemberReference
        - ClassReference

    Args:
        method_declaration: MethodDeclaration node

    Returns:
        Set of method body names concatenated into a string
    """
    body_tokens = set()

    for _, node in method_declaration.filter(javalang.tree.MemberReference):
        body_tokens.update(convert_name_to_tokens(node.member))

    for _, node in method_declaration.filter(javalang.tree.MethodInvocation):
        if node.qualifier:
            body_tokens.update(convert_name_to_tokens(node.qualifier))
        body_tokens.update(convert_name_to_tokens(node.member))

    for _, node in method_declaration.filter(javalang.tree.ClassReference):
        if node.type:
            body_tokens.update(convert_name_to_tokens(node.type.name))

    for _, node in method_declaration.filter(
            javalang.tree.SuperMemberReference):
        body_tokens.update(convert_name_to_tokens(node.member))

    for _, node in method_declaration.filter(
            javalang.tree.SuperMethodInvocation):
        if node.qualifier:
            body_tokens.update(convert_name_to_tokens(node.qualifier))
        body_tokens.update(convert_name_to_tokens(node.member))

    body = ' '.join(body_tokens)

    return body


def get_return_type(method_declaration):
    """Gets the return type from a MethodDeclaration node.

    If the return type is a Python NoneType, the string "void" is produced.

    Args:
        method_declaration: MethodDeclaration node

    Returns:
        The name of the return type as a string
    """
    if method_declaration.return_type:
        return ' '.join(
            convert_name_to_tokens(method_declaration.return_type.name))
    else:
        return 'void'


def get_input_parameters(method_declaration):
    """Gets the input parameters from a MethodDeclaration node.

    Args:
        method_declaration: MethodDeclaration node

    Returns:
        String containing the type and name of each input parameter
    """
    input_parameter_tokens = []

    for parameter in method_declaration.parameters:
        input_parameter_tokens.extend(
            convert_name_to_tokens(parameter.type.name))
        input_parameter_tokens.extend(convert_name_to_tokens(parameter.name))

    input_parameters = ' '.join(input_parameter_tokens)

    return input_parameters


def get_enclosing_classes(path):
    """Creates a list of the enclosing classes of a MethodDeclaration.

    When we apply the javalang filter() method to look for MethodDeclaration
    nodes, we get a list of tuples (in the form of a generator). The first item
    in each tuple is the path to the node, which is also a tuple. In this path
    tuple, we look for the ClassDeclaration nodes and record their names. The
    ordering starts with the highest-level parent class.

    Args:
        path: Path tuple created by the javalang filter() method

    Returns:
        Enclosing class tokens concatenated as a string
    """
    enclosing_class_tokens = []

    for path_step in path:
        if type(path_step) == javalang.tree.ClassDeclaration:
            enclosing_class_tokens.extend(
                convert_name_to_tokens(path_step.name))

    enclosing_classes = ' '.join(enclosing_class_tokens)

    return enclosing_classes


def get_documentation(method_declaration):
    """Gets the Javadoc method summary sentence.

    Following the Oracle Javadoc guidelines (citation [20] in Gao et al.
    paper), the first sentence of a Javadoc comment "should be a summary
    sentence, containing a concise but complete description of the API item."
    This is what Gao et al. extracted as a natural language description of the
    corresponding method name.

    All non-alphanumeric characters will be filtered out.

    Args:
        method_declaration: MethodDeclaration node

    Returns:
        Processed method summary string
    """
    documentation = method_declaration.documentation

    if not documentation:
        return None

    # Remove the @link tags
    documentation = re.sub(r'@link', '', documentation)
    # Remove HTML tags
    documentation = re.sub(r'<[^>]*>', '', documentation)

    # End at first occurrence of "." or "@"
    period_match = re.search(r'\.', documentation)
    at_char_match = re.search(r'@', documentation)

    if period_match and at_char_match:
        end = min(period_match.start(), at_char_match.start())
    elif period_match:
        end = period_match.start()
    elif at_char_match:
        end = at_char_match.start()
    else:
        end = len(documentation)

    documentation = documentation[:end]

    # Replace non-word characters with space
    documentation = re.sub(r'\W', ' ', documentation)

    documentation_tokens = []
    for name in documentation.split():
        documentation_tokens.extend(convert_name_to_tokens(name))

    documentation = ' '.join(documentation_tokens)

    return documentation


def convert_name_to_tokens(name) -> list:
    """Converts a name from snake case or camel case to list of string tokens.

    Args:
        name: Entity name string in snake case or camel case

    Returns:
        list: List of lowercase string tokens
    """
    if name.find('_') > 0:
        return name.lower().split('_')
    else:
        tokens = re.findall(
            r'[a-zA-Z0-9](?:[a-z0-9]+|[A-Z]*(?=[A-Z]|$))', name)
        tokens = list(map(lambda s: s.lower(), tokens))
        return tokens
