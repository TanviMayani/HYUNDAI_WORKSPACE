import React from "react";
import { Box, Typography } from "@mui/material";
import styled from "@emotion/styled";
import CloudUploadIcon from "@mui/icons-material/CloudUploadOutlined";

const VisuallyHiddenInput = styled("input")({
  cursor: "pointer",
  position: "absolute",
  height: "100%",
  opacity: 0,
  width: "100%",
});

const UploadComponent = ({ handleChange }) => {
  return (
    <React.Fragment>
      <Box position={"relative"}>
        <VisuallyHiddenInput
          type="file"
          multiple={true}
          // @ts-expect-error : ignore this error
          directory=""
          webkitdirectory=""
          mozdirectory=""
          allowdirs=""
          msdirectory=""
          odirectory=""
          onChange={handleChange}
        />
        <Box
          sx={{
            textAlign: "center",
            padding: 5,
            width: "100%",
            border: (theme) => `1px dashed ${theme.palette.primary.light}`,
            borderRadius: "8px",
          }}
        >
          <Box display={"flex"} flexDirection={"column"} alignItems={"center"}>
            <CloudUploadIcon
              className="secondary-pink"
              sx={{ fontSize: "4rem" }}
            />
            <Typography>{`Drag & Drop your files here`}</Typography>
            <div className="uploadCaption">
              <span>You can upload a maximum of 5 files</span>
              <span>Each file should not be more than 5 MB</span>
              <span>Only pdf, jpg,jpeg,png allowed</span>
            </div>
          </Box>
        </Box>
      </Box>
    </React.Fragment>
  );
};

export default UploadComponent;
