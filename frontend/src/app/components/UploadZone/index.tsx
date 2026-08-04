import React, { useState } from "react";
import { InputLabel, Typography } from "@mui/material";
import { useTheme } from "@mui/material/styles";
import { UploadFile } from "@mui/icons-material";
import { LOADING_TEXT } from "../../constants";
import toast from "react-hot-toast";

const UploadComponent = ({
  label,
  acceptedFiles = "image/*,application/pdf,.doc,.docx,application/msword,application/vnd.openxmlformats-officedocument.wordprocessingml.document",
  classes,
}: //setDeleteFile
any) => {
  const [fileName, setFileName] = useState<string>("");

  return (
    <div className={classes}>
      <InputLabel
        sx={{
          pb: 1,
          //   color: theme.palette.grey["800"],
        }}
      >
        <span className="text-lg">{label}</span>
      </InputLabel>
      <div className="relative">
        <input
          type="file"
          //onChange={handleFileChange}
          accept={acceptedFiles}
          className="cursor-pointer relative block opacity-0 w-full h-full p-10 z-50"
        />
        <div
          className={`text-center p-6 absolute top-0 right-0 left-0 m-auto border border-dashed border-brand-grey-200`}
        >
          <div className="flex justify-center pb-1">
            <UploadFile fontSize="small" color="primary" />
            <Typography className="text-sm text-grey-800 font-normal">
              {`Upload File`}
            </Typography>
          </div>
        </div>
      </div>
    </div>
  );
};

export default UploadComponent;
