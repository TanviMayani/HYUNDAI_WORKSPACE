import { ChangeEvent } from "react";
import toast from "react-hot-toast";

interface UseFileUploadOptions {
  allowedTypes?: string[];
  maxFileSize?: number;
  multiple?: boolean;
}

const useFileUpload = (
  initialFiles: File[] = [],
  setFiles: (files: File[]) => void,
  options: UseFileUploadOptions = {}
) => {
  const {
    allowedTypes = ["application/pdf"],
    maxFileSize = 20 * 1024 * 1024,
    multiple = true,
  } = options;

  const handleFileChange = (event: ChangeEvent<HTMLInputElement>) => {
    const selectedFiles = Array.from(event.target.files || []);
    let hasError = false;
    const invalidFiles: string[] = [];
    const combinedFiles = multiple ? [...initialFiles] : [];
    if (!multiple && selectedFiles.length > 1) {
      toast.error("Only one file can be selected.");
      return;
    }
    for (const file of selectedFiles) {
      if (!allowedTypes.includes(file.type)) {
        toast.error(`${file.name} is not an allowed file type.`);
        hasError = true;
        invalidFiles.push(file.name);
      } else if (file.size > maxFileSize) {
        toast.error(
          `${file.name} exceeds the ${
            maxFileSize / (1024 * 1024)
          } MB size limit.`
        );
        hasError = true;
        invalidFiles.push(file.name);
      } else {
        combinedFiles.push(file);
      }
    }
    if (hasError) {
      // console.log(`Invalid files: ${invalidFiles.join(", ")}`);
    } else {
      setFiles(combinedFiles);
    }
  };
  return {
    handleFileChange,
  };
};

export default useFileUpload;
