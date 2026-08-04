import { Box, CircularProgress, Typography } from "@mui/material";

const DrawerLoader = () => {
  return (
    <Box
      width="90%"
      height="80vh"
      bgcolor="white"
      position={"absolute"}
      top={0}
      display={"flex"}
      gap={2}
      flexDirection={"column"}
      justifyContent={"center"}
      alignItems={"center"}
      sx={{ opacity: "0.9" }}
      zIndex={99}
    >
      <CircularProgress /> <Typography fontWeight={"bold"} className="secondary-pink">Processing...</Typography>
    </Box>
  );
};

export default DrawerLoader;
