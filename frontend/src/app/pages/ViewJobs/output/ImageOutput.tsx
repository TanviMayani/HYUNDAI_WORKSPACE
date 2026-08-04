import React, { useState } from "react";
import { BoxContainer, NoOutput } from "../OutputViewer";
import FullPopup from "../../../components/Popup/FullPopup";
import { Box, Typography } from "@mui/material";
import { downloadPDF } from "../../../utils/commons/download";
import ContentCopyIcon from "@mui/icons-material/ContentCopy";
import CheckCircleIcon from "@mui/icons-material/CheckCircle";
import { CopyToClipboard } from "react-copy-to-clipboard";
import CheckCircleOutlineIcon from "@mui/icons-material/CheckCircleOutline";
import CancelIcon from "@mui/icons-material/Cancel";

interface ImageOutputProps {
  result: Array<{ url: string; value: string; status: string }>;
  title: string;
}

const ImageOutput: React.FC<ImageOutputProps> = ({
  result,
  title = "Signature",
}) => {
  const [open, setOpen] = useState(false);
  const [copy, setCopy] = useState(false);

  const renderImages = () =>
    result?.length > 0 ? (
      result?.map((item, index) => (
        <Box width="100%" display={"flex"} justifyContent={"center"} mt={3}>
          <Box width="40%">
            <img
              style={{ width: "100%" }}
              key={index}
              src={item.url}
              alt={`Image ${index}`}
            />
            <Box
              display={"flex"}
              justifyContent={"space-between"}
              alignItems={"center"}
              gap={1}
            >
              <Typography className="ellipsis" color="secondary" fontSize={14}>
                {item?.value}
              </Typography>
              <CopyToClipboard text={item?.value} onCopy={() => setCopy(true)}>
                {copy ? <CheckCircleIcon /> : <ContentCopyIcon />}
              </CopyToClipboard>
            </Box>
            <Box
              display={"flex"}
              justifyContent={"space-between"}
              alignItems={"center"}
              gap={1}
              mt={1}
            >
              <Typography color="primary" fontSize={14}>
                Status
              </Typography>
              {item?.status === "Valid" ? (
                <Typography
                  color="secondary"
                  fontSize={14}
                  display={"flex"}
                  alignItems={"center"}
                  gap={0.5}
                >
                  <CheckCircleOutlineIcon />
                  Valid
                </Typography>
              ) : (
                <Typography
                  fontSize={14}
                  display={"flex"}
                  alignItems={"center"}
                  gap={0.5}
                >
                  <CancelIcon sx={{ color: "red" }} />
                  Invalid
                </Typography>
              )}
            </Box>
          </Box>
        </Box>
      ))
    ) : (
      <NoOutput />
    );

  return (
    <BoxContainer
      title={title}
      handleTrue={() => setOpen(true)}
      handleDownload={() => downloadPDF(result[0]?.url, title)}
    >
      {renderImages()}
      <FullPopup open={open} close={() => setOpen(false)} title="Preview">
        <Box maxWidth="900px" mt={3}>
          {result?.length > 0 ? (
            result?.map((item, index) => (
              <Box
                width="100%"
                display={"flex"}
                justifyContent={"center"}
                gap={3}
                mt={3}
              >
                <Box flex={1}>
                  <img
                    style={{ width: "100%" }}
                    key={index}
                    src={item.url}
                    alt={`Image ${index}`}
                  />
                </Box>
                <Box flex={1}>
                  <Box
                    display={"flex"}
                    justifyContent={"space-between"}
                    gap={2}
                    sx={{ wordBreak: "break-all" }}
                  >
                    <Typography color="secondary">{item?.value}</Typography>
                    <CopyToClipboard
                      text={item?.value}
                      onCopy={() => setCopy(true)}
                    >
                      {copy ? <CheckCircleIcon /> : <ContentCopyIcon />}
                    </CopyToClipboard>
                  </Box>
                  <Box
                    display={"flex"}
                    justifyContent={"space-between"}
                    alignItems={"center"}
                    gap={1}
                    mt={2}
                  >
                    <Typography color="primary" fontSize={14}>
                      Status
                    </Typography>
                    {item?.status === "Valid" ? (
                      <Typography
                        color="secondary"
                        fontSize={14}
                        display={"flex"}
                        alignItems={"center"}
                        gap={0.5}
                      >
                        <CheckCircleOutlineIcon />
                        Valid
                      </Typography>
                    ) : (
                      <Typography
                        fontSize={14}
                        display={"flex"}
                        alignItems={"center"}
                        gap={0.5}
                      >
                        <CancelIcon sx={{ color: "red" }} />
                        Invalid
                      </Typography>
                    )}
                  </Box>
                </Box>
              </Box>
            ))
          ) : (
            <NoOutput />
          )}
        </Box>
      </FullPopup>
    </BoxContainer>
  );
};

export default ImageOutput;
