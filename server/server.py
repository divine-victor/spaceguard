from pygls.server import LanguageServer
from lsprotocol.types import TEXT_DOCUMENT_DID_OPEN, TEXT_DOCUMENT_DID_SAVE, TEXT_DOCUMENT_DID_CHANGE, Diagnostic, DiagnosticSeverity, Range, Position
from engine import SpatialAnalyzer 

server = LanguageServer("spaceguard", "v1.0")

def validate_document(ls, params):
    document = ls.workspace.get_text_document(params.text_document.uri)
    source_code = document.source.encode('utf-8')
    
    analyzer = SpatialAnalyzer(source_code)
    issues = analyzer.analyze()
    
    diagnostics = []
    for issue in issues:
        line_idx = issue['line'] - 1
        diag = Diagnostic(
            range=Range(
                start=Position(line=line_idx, character=0),
                end=Position(line=line_idx, character=100)
            ),
            message=issue['message'],
            severity=DiagnosticSeverity.Error,
            source="SpaceGuard"
        )
        diagnostics.append(diag)
        
    ls.publish_diagnostics(document.uri, diagnostics)

server.feature(TEXT_DOCUMENT_DID_OPEN)(validate_document)
server.feature(TEXT_DOCUMENT_DID_SAVE)(validate_document)
server.feature(TEXT_DOCUMENT_DID_CHANGE)(validate_document)

if __name__ == "__main__":
    server.start_io()