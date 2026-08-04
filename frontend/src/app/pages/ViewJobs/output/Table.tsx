import { useState } from "react";
import { BoxContainer, NoOutput } from "../OutputViewer";
import FullPopup from "../../../components/Popup/FullPopup";
import { Box } from "@mui/material";
import { tableToExcel } from "../../../utils/commons/exportToXls";

const TableRenderer = ({ result }) => {
  return (
    <>
      {result?.table?.heading?.length > 0 ? (
        <div className="table-container">
          <table className="responsive-table">
            <thead>
              <tr>
                {result?.table?.heading?.map((ele, i) => (
                  <th key={i}>{ele}</th>
                ))}
              </tr>
            </thead>
            <tbody>
              {result?.table?.rows?.map((ele, rowIndex) => (
                <tr
                  key={rowIndex}
                  className={rowIndex % 2 === 0 ? "even-row" : "odd-row"}
                >
                  {ele?.length > 0 &&
                    ele?.map((atom, cellIndex) => (
                      <td key={cellIndex}>{atom}</td>
                    ))}
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      ) : (
        <NoOutput />
      )}
    </>
  );
};

const Table = ({ result }) => {
  const [open, setOpen] = useState(false);
  return (
    <BoxContainer
      title="Table"
      handleTrue={() => setOpen(true)}
      handleDownload={() => tableToExcel(result?.table)}
    >
      <TableRenderer result={result} />
      <FullPopup open={open} close={() => setOpen(false)} title="Preview">
        <Box maxWidth="1100px" width={"100%"} mt={3}>
          <TableRenderer result={result} />
        </Box>
      </FullPopup>
    </BoxContainer>
  );
};

export default Table;
