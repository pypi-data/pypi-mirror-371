import {
  JupyterFrontEnd,
  JupyterFrontEndPlugin
} from '@jupyterlab/application';

import { INotebookTracker, NotebookPanel } from '@jupyterlab/notebook';

import { CodeCell, ICellModel } from '@jupyterlab/cells';

import { requestAPI } from './handler';

/**
 * Initialization data for the jupy-sqlite-extension extension.
 */
const plugin: JupyterFrontEndPlugin<void> = {
  id: 'jupy-sqlite-extension:plugin',
  description: 'JupyterLab extension for SQLite execution based on cell metadata without magic',
  autoStart: true,
  requires: [INotebookTracker],
  activate: (app: JupyterFrontEnd, notebookTracker: INotebookTracker) => {
    console.log('JupyterLab extension jupy-sqlite-extension is activated!');

    const executeSQLCell = async (cell: CodeCell): Promise<void> => {
      const sqlCell = cell.model.getMetadata('sql_cell');
      const language = cell.model.getMetadata('language');
      const dbFileValue = cell.model.getMetadata('db_file');

      if (sqlCell === true || language === 'sql') {
        const dbFile = dbFileValue as string;

        if (!dbFile) {
          cell.outputArea.model.clear();
          cell.outputArea.model.add({
            output_type: 'error',
            ename: 'SQLiteError',
            evalue: 'Missing db_file in cell metadata',
            traceback: ['SQLiteError: Cell metadata must include "db_file" field']
          });
          return;
        }

        try {
          const sqlCode = cell.model.sharedModel.getSource();
          const result = await requestAPI<any>('execute-sql', {
            method: 'POST',
            body: JSON.stringify({
              sql: sqlCode,
              db_file: dbFile
            }),
            headers: {
              'Content-Type': 'application/json'
            }
          });

          cell.outputArea.model.clear();

          if (result.error) {
            cell.outputArea.model.add({
              output_type: 'error',
              ename: 'SQLiteError',
              evalue: result.error,
              traceback: [result.error]
            });
          } else if (result.formatted_output) {
            // Display pre-formatted table from backend
            cell.outputArea.model.add({
              output_type: 'stream',
              name: 'stdout',
              text: result.formatted_output
            });
          } else if (result.message) {
            // Handle non-SELECT queries
            cell.outputArea.model.add({
              output_type: 'stream',
              name: 'stdout',
              text: result.message
            });
          }
        } catch (error) {
          cell.outputArea.model.clear();
          cell.outputArea.model.add({
            output_type: 'error',
            ename: 'SQLiteError',
            evalue: String(error),
            traceback: [String(error)]
          });
        }
      }
    };

    notebookTracker.widgetAdded.connect((sender: INotebookTracker, widget: NotebookPanel) => {
      const notebook = widget.content;

      const setupCellExecution = (cell: CodeCell) => {
        let lastExecutionCount = cell.model.executionCount;

        cell.model.stateChanged.connect((sender: ICellModel) => {
          const currentExecutionCount = (sender as any).executionCount;
          // Only execute when executionCount actually increases (cell was run)
          if (currentExecutionCount !== null &&
              currentExecutionCount > 0 &&
              currentExecutionCount !== lastExecutionCount) {
            lastExecutionCount = currentExecutionCount;
            executeSQLCell(cell);
          }
        });
      };

      notebook.model!.cells.changed.connect(() => {
        notebook.widgets.forEach((cell) => {
          if (cell instanceof CodeCell) {
            setupCellExecution(cell as CodeCell);
          }
        });
      });

      // Also set up for existing cells
      notebook.widgets.forEach((cell) => {
        if (cell instanceof CodeCell) {
          setupCellExecution(cell as CodeCell);
        }
      });
    });
  }
};

export default plugin;
