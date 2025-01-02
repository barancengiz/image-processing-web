<template>
  <div class="upload-container">
    <h1>Image Processing App</h1>
    <form @submit.prevent="submitForm">
      <div>
        <label for="image">Select an Image:</label>
        <input type="file" id="image" @change="handleFileChange" />
      </div>
      <div>
        <label for="operation">Operation:</label>
        <select id="operation" v-model="operation">
          <option value="resize">Resize</option>
          <option value="grayscale">Grayscale</option>
        </select>
      </div>
      <button type="submit">Process Image</button>
    </form>
    <div v-if="processedImage">
      <h2>Processed Image:</h2>
      <img :src="processedImage" alt="Processed" />
    </div>
  </div>
</template>

<script>
import axios from "axios";

export default {
  data() {
    return {
      file: null,
      operation: "resize",
      processedImage: null,
    };
  },
  methods: {
    handleFileChange(event) {
      this.file = event.target.files[0];
    },
    async submitForm() {
      if (!this.file) {
        alert("Please select a file.");
        return;
      }

      const formData = new FormData();
      formData.append("file", this.file);
      formData.append("operation", this.operation);

      try {
        const response = await axios.post("http://127.0.0.1:8000/process/", formData, {
          headers: {
            "Content-Type": "multipart/form-data",
          },
        });
        // Get path of the processed image from the response
        this.processedImage = response.data.file_path;
      } catch (error) {
        console.error("Error processing the image:", error);
        alert("Failed to process the image.");
      }
    },
  },
};
</script>

<style>
.upload-container {
  max-width: 500px;
  margin: auto;
  text-align: center;
}
</style>