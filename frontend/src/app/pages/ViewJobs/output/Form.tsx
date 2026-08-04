import React, { useState } from "react";
import { BoxContainer, NoOutput } from "../OutputViewer";
import { Box, Divider, Typography, IconButton, Dialog, DialogTitle, DialogContent, DialogActions, Button, TextField, CircularProgress } from "@mui/material";
import FullPopup from "../../../components/Popup/FullPopup";
import { exportToXls } from "../../../utils/commons/exportToXls";
import { isArray } from "lodash";
import FactCheckIcon from '@mui/icons-material/FactCheck';
import { useStringMatchMutation } from "../../../redux/features/jobs";

interface FormProps {
  result: {
    form?: object;
  };
}

const Form: React.FC<FormProps> = ({ result }) => {
  const [open, setOpen] = useState(false);
  const data = result?.form ? Object.entries(result.form) : [];
  
  const [verifyOpen, setVerifyOpen] = useState(false);
  const [verifyField, setVerifyField] = useState("");
  const [extractedValue, setExtractedValue] = useState("");
  const [expectedValue, setExpectedValue] = useState("");
  const [matchPercentage, setMatchPercentage] = useState<string | null>(null);

  const [stringMatch, { isLoading }] = useStringMatchMutation();

  const handleVerifyClick = (key: string, value: any) => {
    setVerifyField(key);
    setExtractedValue(String(value));
    setExpectedValue("");
    setMatchPercentage(null);
    setVerifyOpen(true);
  };

  const handleCompare = async () => {
    if (!expectedValue.trim()) return;
    
    // Auto-remove spaces and hyphens so copy-pasting from PDFs matches perfectly
    const cleanedExpectedValue = expectedValue.replace(/[-\s]/g, '');

    try {
      const res = await stringMatch({ string1: extractedValue, string2: cleanedExpectedValue }).unwrap();
      const percentage = res?.data?.percentage || res?.percentage;
      if (percentage) {
        setMatchPercentage(percentage);
      } else {
        setMatchPercentage("Error");
      }
    } catch (error) {
      console.error("String match error:", error);
      setMatchPercentage("Error");
    }
  };

  const renderFormItems = () => {
    return (
      data?.length > 0 &&
      data?.map(([key, value], index) => {
        const displayValue = typeof value === "string" || typeof value === "number" || isArray(value) ? value : "-";
        return (
          <React.Fragment key={index}>
            <Divider sx={{ mt: 1, background: "#f8f8f8" }} />
            <Box
              display="flex"
              alignItems="center"
              justifyContent={"space-between"}
              mt={1}
            >
              <Box display="flex" alignItems="flex-start" sx={{ flexGrow: 1, maxWidth: "90%" }}>
                <span
                  className="secondary-pink"
                  style={{
                    fontSize: "1.2ch",
                    marginRight: "1em",
                    fontWeight: "bold",
                    minWidth: "30%",
                  }}
                >
                  {key}
                </span>
                <Typography
                  variant="h6"
                  fontSize={"1.2ch"}
                  sx={{ wordBreak: "break-word" }}
                >
                  {displayValue}
                </Typography>
              </Box>
              {displayValue !== "-" && (
                <IconButton size="small" onClick={() => handleVerifyClick(key, displayValue)} title="Verify Field">
                  <FactCheckIcon fontSize="small" color="primary" />
                </IconButton>
              )}
            </Box>
          </React.Fragment>
        );
      })
    );
  };

  return (
    <>
      <BoxContainer
        title="Form"
        handleTrue={() => setOpen(true)}
        handleDownload={() => exportToXls(data)}
      >
        {result?.form ? renderFormItems() : <NoOutput />}
        <FullPopup open={open} close={() => setOpen(false)} title="Preview">
          <Box width="1100px">
            {result?.form ? renderFormItems() : <NoOutput />}
            <Box pb={6}></Box>
          </Box>
        </FullPopup>
      </BoxContainer>

      <Dialog open={verifyOpen} onClose={() => setVerifyOpen(false)} maxWidth="sm" fullWidth>
        <DialogTitle>Verify: {verifyField}</DialogTitle>
        <DialogContent dividers>
          <Box mb={2}>
            <Typography variant="caption" color="textSecondary">Extracted Value (String 1)</Typography>
            <Typography variant="body1" sx={{ wordBreak: "break-word", p: 1, bgcolor: "#f5f5f5", borderRadius: 1 }}>
              {extractedValue}
            </Typography>
          </Box>
          <Box mb={2}>
            <TextField
              fullWidth
              label="Expected Value (String 2)"
              variant="outlined"
              size="small"
              value={expectedValue}
              onChange={(e) => setExpectedValue(e.target.value)}
              placeholder="Paste expected value here..."
            />
          </Box>
          {matchPercentage !== null && (
            <Box p={1.5} borderRadius={1} bgcolor={matchPercentage === "Error" ? "#ffebee" : Number(matchPercentage) >= 90 ? "#e8f5e9" : Number(matchPercentage) >= 70 ? "#fff3e0" : "#ffebee"}>
              <Typography variant="subtitle1" fontWeight="bold" textAlign="center" color={matchPercentage === "Error" ? "error" : Number(matchPercentage) >= 90 ? "success.main" : Number(matchPercentage) >= 70 ? "warning.main" : "error.main"}>
                {matchPercentage === "Error" ? "Failed to verify match." : `Match Percentage: ${matchPercentage}%`}
              </Typography>
            </Box>
          )}
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setVerifyOpen(false)}>Close</Button>
          <Button variant="contained" onClick={handleCompare} disabled={!expectedValue.trim() || isLoading}>
            {isLoading ? <CircularProgress size={24} /> : "Compare"}
          </Button>
        </DialogActions>
      </Dialog>
    </>
  );
};

export default Form;
