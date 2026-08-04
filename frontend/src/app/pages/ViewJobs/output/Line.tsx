import React, { useState } from "react";
import { BoxContainer, NoOutput } from "../OutputViewer";
import { Box, Typography } from "@mui/material";
import { saveAs } from "file-saver";
import FullPopup from "../../../components/Popup/FullPopup";

interface LineProps {
  result: {
    line?: string | undefined;
  };
}

const Line: React.FC<LineProps> = ({ result }) => {
  const [open, setOpen] = useState(false);

  const Content = () =>
    result?.line ? (
      <Typography variant="h6" fontWeight="600" fontSize={16}>
        {result.line}
      </Typography>
    ) : (
      <NoOutput />
    );

  const saveTextAsFile = () => {
    const blob = new Blob([result.line], { type: "text/plain;charset=utf-8" });
    saveAs(blob, `line.txt`);
  };

  return (
    <BoxContainer
      title="Line"
      handleTrue={() => setOpen(true)}
      handleDownload={saveTextAsFile}
    >
      <Content />
      <FullPopup open={open} close={() => setOpen(false)} title="Preview">
        <Box width="900px" mt={3}>
          <Content />
        </Box>
      </FullPopup>
    </BoxContainer>
  );
};

export default Line;
