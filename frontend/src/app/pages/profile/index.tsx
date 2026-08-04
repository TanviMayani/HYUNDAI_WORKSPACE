import React, { useState, useEffect } from "react";
import {
  Box,
  Paper,
  Typography,
  TextField,
  Button,
  Avatar,
  Stack,
  Alert,
  Snackbar,
} from "@mui/material";
import {
  useGetProfileQuery,
  useUpdateProfileMutation,
} from "../../redux/features/profile";

export default function Profile() {
  const { data: profileData, refetch } = useGetProfileQuery({});
  const [updateProfile, { isLoading }] = useUpdateProfileMutation();

  const [firstName, setFirstName] = useState("");
  const [lastName, setLastName] = useState("");
  const [file, setFile] = useState<File | null>(null);
  const [preview, setPreview] = useState<string | null>(null);
  const [successMsg, setSuccessMsg] = useState("");
  const [errorMsg, setErrorMsg] = useState("");

  useEffect(() => {
    if (profileData) {
      setFirstName(profileData.first_name || "");
      setLastName(profileData.last_name || "");
    }
  }, [profileData]);

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files[0]) {
      const selectedFile = e.target.files[0];
      setFile(selectedFile);
      setPreview(URL.createObjectURL(selectedFile));
    }
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    const formData = new FormData();
    if (firstName) formData.append("first_name", firstName);
    if (lastName) formData.append("last_name", lastName);
    if (file) formData.append("file", file);

    try {
      const res = await updateProfile(formData).unwrap();
      setSuccessMsg("Profile updated successfully!");
      setPreview(null);
      setFile(null);
      refetch(); // Fetch latest to update the global state/header
    } catch (err: any) {
      console.error(err);
      setErrorMsg("Failed to update profile. Please try again.");
    }
  };

  return (
    <Box sx={{ p: 4, pt: 10 }}>
      <Typography variant="h4" gutterBottom fontWeight="600">
        My Profile
      </Typography>
      <Paper elevation={0} sx={{ p: 4, maxWidth: 600, borderRadius: 2 }}>
        <form onSubmit={handleSubmit}>
          <Stack spacing={4}>
            <Box display="flex" alignItems="center" gap={3}>
              <Avatar
                src={preview || profileData?.profile_photo || ""}
                sx={{ width: 100, height: 100 }}
              />
              <Button variant="outlined" component="label">
                Upload New Photo
                <input
                  type="file"
                  hidden
                  accept="image/*"
                  onChange={handleFileChange}
                />
              </Button>
            </Box>

            <TextField
              label="First Name"
              value={firstName}
              onChange={(e) => setFirstName(e.target.value)}
              fullWidth
              variant="outlined"
            />

            <TextField
              label="Last Name"
              value={lastName}
              onChange={(e) => setLastName(e.target.value)}
              fullWidth
              variant="outlined"
            />

            <TextField
              label="Email"
              value={profileData?.email || ""}
              disabled
              fullWidth
              variant="outlined"
            />

            <Button
              type="submit"
              variant="contained"
              color="primary"
              disabled={isLoading}
              sx={{ width: 150 }}
            >
              {isLoading ? "Saving..." : "Save Changes"}
            </Button>
          </Stack>
        </form>
      </Paper>

      <Snackbar
        open={!!successMsg}
        autoHideDuration={6000}
        onClose={() => setSuccessMsg("")}
      >
        <Alert severity="success" onClose={() => setSuccessMsg("")}>
          {successMsg}
        </Alert>
      </Snackbar>

      <Snackbar
        open={!!errorMsg}
        autoHideDuration={6000}
        onClose={() => setErrorMsg("")}
      >
        <Alert severity="error" onClose={() => setErrorMsg("")}>
          {errorMsg}
        </Alert>
      </Snackbar>
    </Box>
  );
}
