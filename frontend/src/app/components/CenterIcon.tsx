import { Box } from "@mui/material";
const CenterIcon = ({ children }) => {
  return (
    <Box
      display={"flex"}
      alignItems={"center"}
      justifyContent={"center"}
      className="secondary-bg-pink secondary-pink"
      sx={{ cursor: "pointer" }}
      p={0.5}
      borderRadius={2}
    >
      {children}
    </Box>
  );
};

export default CenterIcon;
