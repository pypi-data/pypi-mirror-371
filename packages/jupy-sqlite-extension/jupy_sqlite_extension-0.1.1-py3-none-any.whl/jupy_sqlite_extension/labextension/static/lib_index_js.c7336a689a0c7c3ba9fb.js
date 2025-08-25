"use strict";
(self["webpackChunkjupy_sqlite_extension"] = self["webpackChunkjupy_sqlite_extension"] || []).push([["lib_index_js"],{

/***/ "./lib/handler.js":
/*!************************!*\
  !*** ./lib/handler.js ***!
  \************************/
/***/ ((__unused_webpack_module, __webpack_exports__, __webpack_require__) => {

__webpack_require__.r(__webpack_exports__);
/* harmony export */ __webpack_require__.d(__webpack_exports__, {
/* harmony export */   requestAPI: () => (/* binding */ requestAPI)
/* harmony export */ });
/* harmony import */ var _jupyterlab_coreutils__WEBPACK_IMPORTED_MODULE_0__ = __webpack_require__(/*! @jupyterlab/coreutils */ "webpack/sharing/consume/default/@jupyterlab/coreutils");
/* harmony import */ var _jupyterlab_coreutils__WEBPACK_IMPORTED_MODULE_0___default = /*#__PURE__*/__webpack_require__.n(_jupyterlab_coreutils__WEBPACK_IMPORTED_MODULE_0__);
/* harmony import */ var _jupyterlab_services__WEBPACK_IMPORTED_MODULE_1__ = __webpack_require__(/*! @jupyterlab/services */ "webpack/sharing/consume/default/@jupyterlab/services");
/* harmony import */ var _jupyterlab_services__WEBPACK_IMPORTED_MODULE_1___default = /*#__PURE__*/__webpack_require__.n(_jupyterlab_services__WEBPACK_IMPORTED_MODULE_1__);


/**
 * Call the API extension
 *
 * @param endPoint API REST end point for the extension
 * @param init Initial values for the request
 * @returns The response body interpreted as JSON
 */
async function requestAPI(endPoint = '', init = {}) {
    // Make request to Jupyter API
    const settings = _jupyterlab_services__WEBPACK_IMPORTED_MODULE_1__.ServerConnection.makeSettings();
    const requestUrl = _jupyterlab_coreutils__WEBPACK_IMPORTED_MODULE_0__.URLExt.join(settings.baseUrl, 'jupy-sqlite-extension', // API Namespace
    endPoint);
    let response;
    try {
        response = await _jupyterlab_services__WEBPACK_IMPORTED_MODULE_1__.ServerConnection.makeRequest(requestUrl, init, settings);
    }
    catch (error) {
        throw new _jupyterlab_services__WEBPACK_IMPORTED_MODULE_1__.ServerConnection.NetworkError(error);
    }
    let data = await response.text();
    if (data.length > 0) {
        try {
            data = JSON.parse(data);
        }
        catch (error) {
            console.log('Not a JSON response body.', response);
        }
    }
    if (!response.ok) {
        throw new _jupyterlab_services__WEBPACK_IMPORTED_MODULE_1__.ServerConnection.ResponseError(response, data.message || data);
    }
    return data;
}


/***/ }),

/***/ "./lib/index.js":
/*!**********************!*\
  !*** ./lib/index.js ***!
  \**********************/
/***/ ((__unused_webpack_module, __webpack_exports__, __webpack_require__) => {

__webpack_require__.r(__webpack_exports__);
/* harmony export */ __webpack_require__.d(__webpack_exports__, {
/* harmony export */   "default": () => (__WEBPACK_DEFAULT_EXPORT__)
/* harmony export */ });
/* harmony import */ var _jupyterlab_notebook__WEBPACK_IMPORTED_MODULE_0__ = __webpack_require__(/*! @jupyterlab/notebook */ "webpack/sharing/consume/default/@jupyterlab/notebook");
/* harmony import */ var _jupyterlab_notebook__WEBPACK_IMPORTED_MODULE_0___default = /*#__PURE__*/__webpack_require__.n(_jupyterlab_notebook__WEBPACK_IMPORTED_MODULE_0__);
/* harmony import */ var _jupyterlab_cells__WEBPACK_IMPORTED_MODULE_1__ = __webpack_require__(/*! @jupyterlab/cells */ "webpack/sharing/consume/default/@jupyterlab/cells");
/* harmony import */ var _jupyterlab_cells__WEBPACK_IMPORTED_MODULE_1___default = /*#__PURE__*/__webpack_require__.n(_jupyterlab_cells__WEBPACK_IMPORTED_MODULE_1__);
/* harmony import */ var _handler__WEBPACK_IMPORTED_MODULE_2__ = __webpack_require__(/*! ./handler */ "./lib/handler.js");



/**
 * Initialization data for the jupy-sqlite-extension extension.
 */
const plugin = {
    id: 'jupy-sqlite-extension:plugin',
    description: 'JupyterLab extension for SQLite execution based on cell metadata without magic',
    autoStart: true,
    requires: [_jupyterlab_notebook__WEBPACK_IMPORTED_MODULE_0__.INotebookTracker],
    activate: (app, notebookTracker) => {
        console.log('JupyterLab extension jupy-sqlite-extension is activated!');
        const executeSQLCell = async (cell) => {
            const sqlCell = cell.model.getMetadata('sql_cell');
            const language = cell.model.getMetadata('language');
            const dbFileValue = cell.model.getMetadata('db_file');
            if (sqlCell === true || language === 'sql') {
                const dbFile = dbFileValue;
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
                    const result = await (0,_handler__WEBPACK_IMPORTED_MODULE_2__.requestAPI)('execute-sql', {
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
                    }
                    else if (result.formatted_output) {
                        // Display pre-formatted table from backend
                        cell.outputArea.model.add({
                            output_type: 'stream',
                            name: 'stdout',
                            text: result.formatted_output
                        });
                    }
                    else if (result.message) {
                        // Handle non-SELECT queries
                        cell.outputArea.model.add({
                            output_type: 'stream',
                            name: 'stdout',
                            text: result.message
                        });
                    }
                }
                catch (error) {
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
        notebookTracker.widgetAdded.connect((sender, widget) => {
            const notebook = widget.content;
            const setupCellExecution = (cell) => {
                let lastExecutionCount = cell.model.executionCount;
                cell.model.stateChanged.connect((sender) => {
                    const currentExecutionCount = sender.executionCount;
                    // Only execute when executionCount actually increases (cell was run)
                    if (currentExecutionCount !== null &&
                        currentExecutionCount > 0 &&
                        currentExecutionCount !== lastExecutionCount) {
                        lastExecutionCount = currentExecutionCount;
                        executeSQLCell(cell);
                    }
                });
            };
            notebook.model.cells.changed.connect(() => {
                notebook.widgets.forEach((cell) => {
                    if (cell instanceof _jupyterlab_cells__WEBPACK_IMPORTED_MODULE_1__.CodeCell) {
                        setupCellExecution(cell);
                    }
                });
            });
            // Also set up for existing cells
            notebook.widgets.forEach((cell) => {
                if (cell instanceof _jupyterlab_cells__WEBPACK_IMPORTED_MODULE_1__.CodeCell) {
                    setupCellExecution(cell);
                }
            });
        });
    }
};
/* harmony default export */ const __WEBPACK_DEFAULT_EXPORT__ = (plugin);


/***/ })

}]);
//# sourceMappingURL=lib_index_js.c7336a689a0c7c3ba9fb.js.map