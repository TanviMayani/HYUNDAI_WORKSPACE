import { Grid } from "@mui/material";
import FileUploadCard from "../../components/FileUploadCard.js";

const PdfCard = ({ data, onItemChange }) => {
  const handleDataChange = (newData) => {
    onItemChange(newData);
  };

  return (
    <>
      <Grid container maxHeight={"35vh"} overflow={"auto"} gap={2} mt={4}>
        {data.length > 0 &&
          Object.values(data).map((item, index) => {
            return (
              <>
                <Grid item xs={12} md={5.87}>
                  <FileUploadCard
                    item={item}
                    key={index}
                    onDataChange={handleDataChange}
                  />
                </Grid>
              </>
            );
          })}
      </Grid>
    </>
  );
};

export default PdfCard;
