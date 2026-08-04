import * as React from "react";
import CloseIcon from "@mui/icons-material/Close";
import {
  Box,
  IconButton,
  Typography,
  Button,
  Dialog,
  AppBar,
  Toolbar,
} from "@mui/material";
import FullscreenExitIcon from "@mui/icons-material/FullscreenExit";
import CenterIcon from "../CenterIcon";
import { Slide, SlideProps } from "@mui/material";

const Transition = React.forwardRef<HTMLDivElement, SlideProps>(
  function Transition(props, ref) {
    return <Slide direction="up" ref={ref} {...props} />;
  }
);

interface FullPopupProps {
  open: boolean;
  close: () => void;
  children: React.ReactNode;
  title: string | undefined;
}

export default function FullPopup({
  open,
  close,
  children,
  title,
}: FullPopupProps) {
  return (
    <React.Fragment>
      <Dialog
        fullScreen
        open={open}
        onClose={close}
        TransitionComponent={Transition}
        PaperProps={{
          style: {
            backgroundColor: "white",
          } as React.CSSProperties, // Ensure this is properly typed
        }}
      >
        <AppBar
          sx={{ position: "sticky", boxShadow: "none", bgcolor: "white" }}
        >
          <Toolbar>
            <IconButton
              edge="start"
              color="inherit"
              onClick={close}
              aria-label="close"
            >
              <CloseIcon className="secondary-pink" />
            </IconButton>
            <Typography
              sx={{ ml: 2, flex: 1 }}
              variant="h6"
              component="div"
              className="secondary-pink"
            >
              {title}
            </Typography>
            <Button autoFocus color="inherit" onClick={close}>
              <CenterIcon>
                <FullscreenExitIcon />
              </CenterIcon>
            </Button>
          </Toolbar>
        </AppBar>
        <Box
          height="100%"
          display="flex"
          justifyContent="center"
          sx={{ bgcolor: "white" }}
        >
          {children}
        </Box>
      </Dialog>
    </React.Fragment>
  );
}
