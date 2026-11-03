import * as path from 'path';
import { workspace, ExtensionContext } from 'vscode';
import { LanguageClient, LanguageClientOptions, ServerOptions } from 'vscode-languageclient/node';

let client: LanguageClient;

export function activate(context: ExtensionContext) {
    // Point to the compiled server.exe instead of Python
    let serverOptions: ServerOptions = {
        command: path.join(context.extensionPath, 'server_bin', 'server.exe')
    };

    let clientOptions: LanguageClientOptions = {
        documentSelector: [{ scheme: 'file', language: 'c' }],
        synchronize: {
            fileEvents: workspace.createFileSystemWatcher('**/*.c')
        },
        outputChannelName: 'SpaceGuard Engine'
    };

    client = new LanguageClient(
        'spaceGuardServer',
        'SpaceGuard Engine',
        serverOptions,
        clientOptions
    );

    client.start();
}

export function deactivate(): Thenable<void> | undefined {
    if (!client) { return undefined; }
    return client.stop();
}