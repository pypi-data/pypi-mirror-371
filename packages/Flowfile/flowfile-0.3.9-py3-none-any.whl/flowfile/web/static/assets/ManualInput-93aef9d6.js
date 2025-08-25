import { N as NodeButton, a as NodeTitle } from "./nodeTitle-a16db7c3.js";
import { r as ref, d as defineComponent, l as computed, m as watch, b as resolveComponent, c as openBlock, e as createElementBlock, f as createVNode, w as withCtx, p as createBaseVNode, F as Fragment, q as renderList, a5 as withDirectives, a6 as vModelText, u as unref, h as createBlock, g as createTextVNode, s as normalizeClass, t as toDisplayString, i as createCommentVNode, E as ElNotification, _ as _export_sfc, n as onMounted, R as nextTick, a7 as Teleport } from "./index-683fc198.js";
import { u as useNodeStore } from "./vue-codemirror.esm-dc5e3348.js";
import { G as GenericNodeSettings } from "./genericNodeSettings-def5879b.js";
import "./designer-6c322d8e.js";
const createManualInput = (flowId = -1, nodeId = -1, pos_x = 0, pos_y = 0) => {
  const nodeManualInput = ref({
    flow_id: flowId,
    node_id: nodeId,
    pos_x,
    pos_y,
    cache_input: false,
    raw_data_format: { columns: [], data: [] },
    cache_results: false
    // Add the missing property 'cache_results'
  });
  return nodeManualInput;
};
const _hoisted_1 = { key: 0 };
const _hoisted_2 = { class: "settings-section" };
const _hoisted_3 = { class: "table-container" };
const _hoisted_4 = { class: "modern-table" };
const _hoisted_5 = ["onClick"];
const _hoisted_6 = { class: "column-header" };
const _hoisted_7 = ["onUpdate:modelValue"];
const _hoisted_8 = ["onUpdate:modelValue"];
const _hoisted_9 = ["onClick"];
const _hoisted_10 = { class: "controls-section" };
const _hoisted_11 = { class: "button-group" };
const _hoisted_12 = {
  key: 0,
  class: "raw-data-section"
};
const _hoisted_13 = { class: "raw-data-controls" };
const _sfc_main$1 = /* @__PURE__ */ defineComponent({
  __name: "manualInput",
  setup(__props, { expose: __expose }) {
    const nodeStore = useNodeStore();
    const dataLoaded = ref(false);
    const nodeManualInput = ref(null);
    const columns = ref([]);
    const rows = ref([]);
    const showRawData = ref(false);
    const rawDataString = ref("");
    let nextColumnId = 1;
    let nextRowId = 1;
    const dataTypes = nodeStore.getDataTypes();
    const rawData = computed(() => {
      return rows.value.map((row) => {
        const obj = {};
        for (const col of columns.value) {
          obj[col.name] = row.values[col.id];
        }
        return obj;
      });
    });
    const rawDataFormat = computed(() => {
      const formattedColumns = columns.value.map((col) => ({
        name: col.name,
        data_type: col.dataType || "String"
      }));
      const data = columns.value.map(
        (col) => rows.value.map((row) => row.values[col.id] || "")
      );
      return {
        columns: formattedColumns,
        data
      };
    });
    const initializeEmptyTable = () => {
      rows.value = [{ id: 1, values: { 1: "" } }];
      columns.value = [{ id: 1, name: "Column 1", dataType: "String" }];
      nextColumnId = 2;
      nextRowId = 2;
    };
    const populateTableFromData = (data) => {
      rows.value = [];
      columns.value = [];
      data.forEach((item, rowIndex) => {
        const row = { id: rowIndex + 1, values: {} };
        Object.keys(item).forEach((key, colIndex) => {
          if (rowIndex === 0) {
            columns.value.push({ id: colIndex + 1, name: key, dataType: "String" });
          }
          row.values[colIndex + 1] = item[key];
        });
        rows.value.push(row);
      });
      nextColumnId = columns.value.length + 1;
      nextRowId = rows.value.length + 1;
    };
    const populateTableFromRawDataFormat = (rawDataFormat2) => {
      var _a;
      rows.value = [];
      columns.value = [];
      if (rawDataFormat2.columns) {
        rawDataFormat2.columns.forEach((col, index) => {
          columns.value.push({
            id: index + 1,
            name: col.name,
            dataType: col.data_type || "String"
          });
        });
      }
      const numRows = ((_a = rawDataFormat2.data[0]) == null ? void 0 : _a.length) || 0;
      for (let rowIndex = 0; rowIndex < numRows; rowIndex++) {
        const row = { id: rowIndex + 1, values: {} };
        rawDataFormat2.data.forEach((colData, colIndex) => {
          row.values[colIndex + 1] = String(colData[rowIndex] || "");
        });
        rows.value.push(row);
      }
      if (numRows === 0 && columns.value.length > 0) {
        const emptyRow = { id: 1, values: {} };
        columns.value.forEach((col) => {
          emptyRow.values[col.id] = "";
        });
        rows.value.push(emptyRow);
        nextRowId = 2;
      } else {
        nextRowId = numRows + 1;
      }
      nextColumnId = columns.value.length + 1;
    };
    const loadNodeData = async (nodeId) => {
      const nodeResult = await nodeStore.getNodeData(nodeId, false);
      if (nodeResult == null ? void 0 : nodeResult.setting_input) {
        nodeManualInput.value = nodeResult.setting_input;
        if (nodeResult.setting_input.raw_data_format && nodeResult.setting_input.raw_data_format.columns && nodeResult.setting_input.raw_data_format.data) {
          populateTableFromRawDataFormat(nodeResult.setting_input.raw_data_format);
        } else if (nodeResult.setting_input.raw_data) {
          populateTableFromData(nodeResult.setting_input.raw_data);
        } else {
          initializeEmptyTable();
        }
      } else {
        nodeManualInput.value = createManualInput(nodeStore.flow_id, nodeStore.node_id).value;
        initializeEmptyTable();
      }
      rawDataString.value = JSON.stringify(rawData.value, null, 2);
      dataLoaded.value = true;
    };
    const addColumn = () => {
      columns.value.push({
        id: nextColumnId,
        name: `Column ${nextColumnId}`,
        dataType: "String"
      });
      nextColumnId++;
    };
    const addRow = () => {
      const newRow = { id: nextRowId, values: {} };
      columns.value.forEach((col) => {
        newRow.values[col.id] = "";
      });
      rows.value.push(newRow);
      nextRowId++;
    };
    const deleteColumn = (id) => {
      const index = columns.value.findIndex((col) => col.id === id);
      if (index !== -1) {
        columns.value.splice(index, 1);
        rows.value.forEach((row) => {
          delete row.values[id];
        });
      }
    };
    const deleteRow = (id) => {
      const index = rows.value.findIndex((row) => row.id === id);
      if (index !== -1) {
        rows.value.splice(index, 1);
      }
    };
    const toggleRawData = () => {
      showRawData.value = !showRawData.value;
    };
    const updateTableFromRawData = () => {
      try {
        const newData = JSON.parse(rawDataString.value);
        if (!Array.isArray(newData)) {
          ElNotification({
            title: "Error",
            message: "Data must be an array of objects",
            type: "error"
          });
          return;
        }
        populateTableFromData(newData);
        ElNotification({
          title: "Success",
          message: "Table updated successfully",
          type: "success"
        });
      } catch (error) {
        ElNotification({
          title: "Error",
          message: "Invalid JSON format. Please check your input.",
          type: "error"
        });
      }
    };
    const pushNodeData = async () => {
      if (nodeManualInput.value) {
        nodeManualInput.value.raw_data_format = rawDataFormat.value;
        await nodeStore.updateSettings(nodeManualInput);
      }
      dataLoaded.value = false;
    };
    watch(rawData, (newVal) => {
      rawDataString.value = JSON.stringify(newVal, null, 2);
    });
    __expose({
      loadNodeData,
      pushNodeData
    });
    return (_ctx, _cache) => {
      const _component_el_option = resolveComponent("el-option");
      const _component_el_select = resolveComponent("el-select");
      const _component_el_button = resolveComponent("el-button");
      const _component_el_input = resolveComponent("el-input");
      const _component_el_collapse_transition = resolveComponent("el-collapse-transition");
      return dataLoaded.value && nodeManualInput.value ? (openBlock(), createElementBlock("div", _hoisted_1, [
        createVNode(GenericNodeSettings, {
          modelValue: nodeManualInput.value,
          "onUpdate:modelValue": _cache[1] || (_cache[1] = ($event) => nodeManualInput.value = $event)
        }, {
          default: withCtx(() => [
            createBaseVNode("div", _hoisted_2, [
              createBaseVNode("div", _hoisted_3, [
                createBaseVNode("table", _hoisted_4, [
                  createBaseVNode("thead", null, [
                    createBaseVNode("tr", null, [
                      (openBlock(true), createElementBlock(Fragment, null, renderList(columns.value, (col) => {
                        return openBlock(), createElementBlock("td", {
                          key: "delete-" + col.id
                        }, [
                          createBaseVNode("button", {
                            class: "delete-button",
                            onClick: ($event) => deleteColumn(col.id)
                          }, null, 8, _hoisted_5)
                        ]);
                      }), 128))
                    ]),
                    createBaseVNode("tr", null, [
                      (openBlock(true), createElementBlock(Fragment, null, renderList(columns.value, (col) => {
                        return openBlock(), createElementBlock("th", {
                          key: col.id
                        }, [
                          createBaseVNode("div", _hoisted_6, [
                            withDirectives(createBaseVNode("input", {
                              "onUpdate:modelValue": ($event) => col.name = $event,
                              class: "input-header",
                              type: "text"
                            }, null, 8, _hoisted_7), [
                              [vModelText, col.name]
                            ]),
                            createVNode(_component_el_select, {
                              modelValue: col.dataType,
                              "onUpdate:modelValue": ($event) => col.dataType = $event,
                              size: "small",
                              class: "type-select"
                            }, {
                              default: withCtx(() => [
                                (openBlock(true), createElementBlock(Fragment, null, renderList(unref(dataTypes), (dtype) => {
                                  return openBlock(), createBlock(_component_el_option, {
                                    key: dtype,
                                    label: dtype,
                                    value: dtype
                                  }, null, 8, ["label", "value"]);
                                }), 128))
                              ]),
                              _: 2
                            }, 1032, ["modelValue", "onUpdate:modelValue"])
                          ])
                        ]);
                      }), 128))
                    ])
                  ]),
                  createBaseVNode("tbody", null, [
                    (openBlock(true), createElementBlock(Fragment, null, renderList(rows.value, (row) => {
                      return openBlock(), createElementBlock("tr", {
                        key: row.id
                      }, [
                        (openBlock(true), createElementBlock(Fragment, null, renderList(columns.value, (col) => {
                          return openBlock(), createElementBlock("td", {
                            key: col.id
                          }, [
                            withDirectives(createBaseVNode("input", {
                              "onUpdate:modelValue": ($event) => row.values[col.id] = $event,
                              class: "input-cell",
                              type: "text"
                            }, null, 8, _hoisted_8), [
                              [vModelText, row.values[col.id]]
                            ])
                          ]);
                        }), 128)),
                        createBaseVNode("td", null, [
                          createBaseVNode("button", {
                            class: "delete-button",
                            onClick: ($event) => deleteRow(row.id)
                          }, null, 8, _hoisted_9)
                        ])
                      ]);
                    }), 128))
                  ])
                ])
              ]),
              createBaseVNode("div", _hoisted_10, [
                createBaseVNode("div", _hoisted_11, [
                  createVNode(_component_el_button, {
                    type: "primary",
                    size: "small",
                    onClick: addColumn
                  }, {
                    icon: withCtx(() => _cache[2] || (_cache[2] = [
                      createBaseVNode("i", { class: "fas fa-plus" }, null, -1)
                    ])),
                    default: withCtx(() => [
                      _cache[3] || (_cache[3] = createTextVNode(" Add Column "))
                    ]),
                    _: 1,
                    __: [3]
                  }),
                  createVNode(_component_el_button, {
                    type: "primary",
                    size: "small",
                    onClick: addRow
                  }, {
                    icon: withCtx(() => _cache[4] || (_cache[4] = [
                      createBaseVNode("i", { class: "fas fa-plus" }, null, -1)
                    ])),
                    default: withCtx(() => [
                      _cache[5] || (_cache[5] = createTextVNode(" Add Row "))
                    ]),
                    _: 1,
                    __: [5]
                  }),
                  createVNode(_component_el_button, {
                    type: "primary",
                    size: "small",
                    onClick: toggleRawData
                  }, {
                    icon: withCtx(() => [
                      createBaseVNode("i", {
                        class: normalizeClass(showRawData.value ? "fas fa-eye-slash" : "fas fa-eye")
                      }, null, 2)
                    ]),
                    default: withCtx(() => [
                      createTextVNode(" " + toDisplayString(showRawData.value ? "Hide" : "Show") + " Raw Data ", 1)
                    ]),
                    _: 1
                  })
                ])
              ]),
              createVNode(_component_el_collapse_transition, null, {
                default: withCtx(() => [
                  showRawData.value ? (openBlock(), createElementBlock("div", _hoisted_12, [
                    createVNode(_component_el_input, {
                      modelValue: rawDataString.value,
                      "onUpdate:modelValue": _cache[0] || (_cache[0] = ($event) => rawDataString.value = $event),
                      type: "textarea",
                      rows: 8,
                      placeholder: JSON.stringify({ column1: "value1" }, null, 2)
                    }, null, 8, ["modelValue", "placeholder"]),
                    createBaseVNode("div", _hoisted_13, [
                      createVNode(_component_el_button, {
                        type: "primary",
                        size: "small",
                        onClick: updateTableFromRawData
                      }, {
                        default: withCtx(() => _cache[6] || (_cache[6] = [
                          createTextVNode(" Update Table ")
                        ])),
                        _: 1,
                        __: [6]
                      })
                    ])
                  ])) : createCommentVNode("", true)
                ]),
                _: 1
              })
            ])
          ]),
          _: 1
        }, 8, ["modelValue"])
      ])) : createCommentVNode("", true);
    };
  }
});
const manualInput_vue_vue_type_style_index_0_scoped_2eba6653_lang = "";
const manualInput = /* @__PURE__ */ _export_sfc(_sfc_main$1, [["__scopeId", "data-v-2eba6653"]]);
const _sfc_main = /* @__PURE__ */ defineComponent({
  __name: "ManualInput",
  props: {
    nodeId: {
      type: Number,
      required: true
    }
  },
  setup(__props) {
    const nodeStore = useNodeStore();
    const nodeButton = ref(null);
    const childComp = ref(null);
    const props = __props;
    const el = ref(null);
    const drawer = ref(false);
    const closeOnDrawer = () => {
      var _a;
      drawer.value = false;
      (_a = childComp.value) == null ? void 0 : _a.pushNodeData();
      nodeStore.isDrawerOpen = false;
    };
    const openDrawer = async () => {
      if (nodeStore.node_id === props.nodeId) {
        return;
      }
      nodeStore.closeDrawer();
      drawer.value = true;
      const drawerOpen = nodeStore.isDrawerOpen;
      nodeStore.isDrawerOpen = true;
      await nextTick();
      if (nodeStore.node_id === props.nodeId && drawerOpen) {
        return;
      }
      if (childComp.value) {
        childComp.value.loadNodeData(props.nodeId);
        nodeStore.openDrawer(closeOnDrawer);
      }
    };
    onMounted(async () => {
      await nextTick();
    });
    return (_ctx, _cache) => {
      return openBlock(), createElementBlock("div", {
        ref_key: "el",
        ref: el
      }, [
        createVNode(NodeButton, {
          ref_key: "nodeButton",
          ref: nodeButton,
          "node-id": __props.nodeId,
          "image-src": "manual_input.png",
          title: `${__props.nodeId}: Manual input`,
          onClick: openDrawer
        }, null, 8, ["node-id", "title"]),
        drawer.value ? (openBlock(), createBlock(Teleport, {
          key: 0,
          to: "#nodesettings"
        }, [
          createVNode(NodeTitle, {
            title: "Provide manual input",
            intro: "Provide a fixed data that can be used and combined with other tables."
          }),
          createVNode(manualInput, {
            ref_key: "childComp",
            ref: childComp,
            "node-id": __props.nodeId
          }, null, 8, ["node-id"])
        ])) : createCommentVNode("", true)
      ], 512);
    };
  }
});
export {
  _sfc_main as default
};
