export function extractDataFromUrl(url) {
  try {
    const urlObj = new URL(url);
    const pathname = urlObj.pathname;
    const fileName = pathname.split("/").pop();
    return decodeURIComponent(fileName);
  } catch (error) {
    console.error("Invalid URL or error extracting file name:", error);
    return null;
  }
}

const getDynamicLength = () => {
  const width = window.innerWidth; // Get the viewport width
  // Define your truncation logic based on width
  if (width > 1200) return 25; // Large screens
  if (width > 1000) return 20;  // Medium screens
  if (width > 500) return 15;  // Medium screens

  return 15;                   // Small screens
};

export const truncate = (data) => {
  const length = getDynamicLength(); // Get dynamic length based on screen size
  const str = data?.length < length ? data : data?.substring(0, length) + "...";
  return str;
};

export const truncateWord = (data, length) => {
  const str = data?.length < length ? data : data?.substring(0, length) + "...";
  return str;
};

export function formatBytes(bytes, decimals = 2) {
  const KB = 1024;
  const MB = KB * 1024;

  if (bytes >= MB) {
    const mb = bytes / MB;
    return `${mb.toFixed(decimals)} MB`;
  } else {
    const kb = bytes / KB;
    return `${kb.toFixed(decimals)} KB`;
  }
}
