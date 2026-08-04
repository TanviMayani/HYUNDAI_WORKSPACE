import * as React from "react";
import Box from "@mui/material/Box";
import { GridRowModesModel, DataGrid } from "@mui/x-data-grid";

export default function DataTable({ columns, rows }) {
  const [allRows, setRows] = React.useState([]);
  const [rowModesModel, setRowModesModel] = React.useState<GridRowModesModel>(
    {}
  );

  React.useEffect(() => {
    setRows(rows);
  }, [rows]);

  return (
    <Box
      sx={{
        height: 500,
        width: "100%",
        "& .actions": {
          color: "text.secondary",
        },
        "& .textPrimary": {
          color: "text.primary",
        },
      }}
    >
      <DataGrid
        rows={allRows}
        columns={columns}
        editMode="row"
        rowModesModel={rowModesModel}
        sx={{
          border: 0,
          "&.MuiDataGrid-root": {
            border: "none",
          },
          "& .MuiDataGrid-columnHeaders": {
            border: "1px solid black",
            borderRadius: "8px",
            background: "#f1f1f1",
            marginBottom: "10px",
          },
          "& .MuiDataGrid-row": {
            boxShadow: "0px 0px 0px 12px rgba(0,0,0,0.01)",
            margin: "8px 0px",

            borderRadius: "8px",
          },
        }}
        // slots={{ toolbar: GridToolbar }}
        slotProps={{
          toolbar: { setRows, setRowModesModel, showQuickFilter: true },
        }}
      />
    </Box>
  );
}
