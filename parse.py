import javalang
import re


NAME = 'name'
DOCUMENTATION = 'documentation'
ENCLOSING_CLASSES = 'enclosing_classes'
INPUT_PARAMETERS = 'input_parameters'
RETURN_TYPE = 'return_type'
BODY_NAMES = 'body_names'

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

    with open(source_file_path) as source_file:
        source = source_file.read()
        
    tree = javalang.parse.parse(source)

    methods = []

    for path, node in tree.filter(javalang.tree.MethodDeclaration):
        name = node.name
        documentation = get_documentation(node)
        
        if documentation:
            enclosing_classes = get_enclosing_classes(path)
            input_parameters = get_input_parameters(node)
            return_type = get_return_type(node)
            body_names = get_body_names(node)

            method = {
                NAME: name,
                DOCUMENTATION: documentation,
                ENCLOSING_CLASSES: enclosing_classes,
                INPUT_PARAMETERS: input_parameters,
                RETURN_TYPE: return_type,
                BODY_NAMES: body_names,
            }
            methods.append(method)

    return methods


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
        tokens = re.findall(r'[a-zA-Z](?:[a-z]+|[A-Z]*(?=[A-Z]|$))', name)
        tokens = list(map(lambda s: s.lower(), tokens))
        return tokens


def get_body_names(method_declaration):
    """Gets the method body names from a MethodDeclaration node.

    There are several types of nodes that include relevant method body names,
    two of which are MemberReference and MethodInvocation. We should attempt to
    include all possible node types. Applying filters individually causes us to
    append the names out of order, which may cause adverse results. 

    look backward in the path, to order the variables. or Depth first search in tree to order them.
    OR turn list to set. body_names = set
    Args:
        method_declaration: MethodDeclaration node

    Returns:
        A list of method body names as strings

        class MemberReference(Primary):
        class MethodInvocation(Invocation):
        class SuperMethodInvocation(Invocation):
        class SuperMemberReference(Primary):
        class ClassReference(Primary):
    """
    body_names = []
    
    for _, node in method_declaration.filter(javalang.tree.MemberReference):
        try:
            body_names.extend(convert_name_to_tokens(node.member))
        except:
            print("MemberReference, object has no attribute member")

    for _, node in method_declaration.filter(javalang.tree.MethodInvocation):
        try:
            if node.qualifier:
                body_names.extend(convert_name_to_tokens(node.qualifier))
            body_names.extend(convert_name_to_tokens(node.member))
        except:
            print("MethodInvocation, object has no attribute member")
    
    for _, node in method_declaration.filter(javalang.tree.ClassReference):
        try:
            body_names.extend(convert_name_to_tokens(node.member))
        except:
            print("ClassReference, object has no attribute member")
            #weird error here: javalang.parser.JavaSyntaxError

    for _, node in method_declaration.filter(javalang.tree.SuperMemberReference):
        try:
            body_names.extend(convert_name_to_tokens(node.member))
        except:
            print("SuperMemberReference, object has no attribute member")

    for _, node in method_declaration.filter(javalang.tree.SuperMethodInvocation):
        try:
            if node.qualifier:
                body_names.extend(convert_name_to_tokens(node.qualifier))
            body_names.extend(convert_name_to_tokens(node.member))
        except:
            print("SuperMethodInvocation, object has no attribute member")
    
    
    return body_names


def get_return_type(method_declaration):
    """Gets the return type from a MethodDeclaration node.

    If the return type is a Python NoneType, the string "void" is produced.

    Args:
        method_declaration: MethodDeclaration node

    Returns:
        The name of the return type as a string
    """
    if method_declaration.return_type:
        return method_declaration.return_type.name
    else:
        return 'void'


def get_input_parameters(method_declaration):
    """Gets the input parameters from a MethodDeclaration node.

    Args:
        method_declaration: MethodDeclaration node

    Returns:
        A list of tuples, containing the name and type of each input parameter
        as strings
    """
    input_parameters = []

    for parameter in method_declaration.parameters:
        input_parameters.append((parameter.name, parameter.type.name))

    return input_parameters


def get_enclosing_classes(path):
    """Creates a list of the enclosing classes of a MethodDeclaration.

    When we apply the javalang filter() method to look for MethodDeclaration
    nodes, we get a list of tuples (in the form of a generator). The first item
    in each tuple is the path to the node, which is also a tuple. In this path
    tuple, the ClassDeclaration (or InterfaceDeclaration) nodes are located at
    every other index, starting at index 2. So, we jump through the path tuple
    as such and extract the names of these nodes to get the enclosing
    class/interface names. The ordering starts with the highest-level parent
    class/interface.
    
    Args:
        path: Path tuple created by the javalang filter() method

    Returns:
        A list of the names of the enclosing classes as strings
    """
    enclosing_classes = []
    
    for i in range(2, len(path), 2):
        try:
            enclosing_classes.append(path[i].name)
        except:
            print("get_enclosing_classes, object has no 'path[i].name")
    
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
        _description_
    """
    documentation = method_declaration.documentation

    if not documentation:
        return None

    start = documentation.find(next(filter(str.isalnum, documentation)))
    documentation = documentation[start:]

    end = documentation.find('.')
    if end < 0:
        end = documentation.find('\n')
    documentation = documentation[:end]

    documentation = re.sub(r'[^a-zA-Z0-9]', ' ', documentation)
    documentation = documentation.lower()

    documentation_tokens = documentation.split()

    return documentation_tokens
