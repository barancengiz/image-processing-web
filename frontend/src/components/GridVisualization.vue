<template>
    <div class="reset-container">
        <button @click="resetZoom">Reset View</button>
        <button @click="zoomIn">Zoom In</button>
        <button @click="zoomOut">Zoom Out</button>
    </div>
    <div class="visualization-container" 
    @wheel="handleZoom"
    @mousedown="startPan"
       @mousemove="pan"
       @mouseup="stopPan"
       @mouseleave="stopPan"
       @dragstart="preventDefault"
       @drag="preventDefault"
       @dragend="preventDefault"
       @drop="preventDefault"
       @keydown="preventDefault"
       @keyup="preventDefault"
       @click="preventDefault">
    <div class="canvas-container" :style="transformStyle">
      <canvas ref="gridCanvas"></canvas>
      <img :src="imageUrl" ref="image" @load="drawGrid" class="grid-image" />
    </div>
  </div>
</template>

<script>
export default {
  props: {
    imageUrl: String,
    pixelWidth: {
      type: Number,
      required: true
    }
  },
  data() {
    return {
      scale: 1,
      panX: 0,
      panY: 0,
      isPanning: false,
      lastX: 0,
      lastY: 0,
      ctx: null,
      canvas: null
    }
  },
  computed: {
    transformStyle() {
      return {
        transform: `scale(${this.scale}) translate(${this.panX}px, ${this.panY}px)`,
        transformOrigin: '0 0',
        imageRendering: 'pixelated'
      }
    }
  },

  methods: {
    resetZoom() {
      this.scale = 1;
      this.panX = 0;
      this.panY = 0;
      this.drawGrid();
    },
    zoomIn() {
      this.scale *= 1.1;
      // Limit zoom levels
      this.scale = Math.min(Math.max(0.1, this.scale), 10);
      // Make scale times width a whole number
      this.scale = Math.round(this.scale * this.$refs.image.width) / this.$refs.image.width;
      this.drawGrid();
    },
    zoomOut() {
      this.scale *= 0.9;
      // Limit zoom levels
      this.scale = Math.min(Math.max(0.1, this.scale), 10);
      // Make scale times width a whole number
      this.scale = Math.round(this.scale * this.$refs.image.width) / this.$refs.image.width;
      this.drawGrid();
    },
    handleZoom(event) {
      event.preventDefault();
      const zoomFactor = event.deltaY > 0 ? 0.9 : 1.1;
      this.scale *= zoomFactor;
      
      // Limit zoom levels
      this.scale = Math.min(Math.max(0.1, this.scale), 10);

      // Make scale times width a whole number
      this.scale = Math.round(this.scale * this.$refs.image.width) / this.$refs.image.width;
      
      this.drawGrid();
    },
    startPan(event) {
      this.isPanning = true;
      this.lastX = event.clientX;
      this.lastY = event.clientY;
    },
    pan(event) {
      if (!this.isPanning) return;
      
      const deltaX = (event.clientX - this.lastX) / this.scale;
      const deltaY = (event.clientY - this.lastY) / this.scale;
      
      this.panX += deltaX;
      this.panY += deltaY;
      
      this.lastX = event.clientX;
      this.lastY = event.clientY;
    },
    stopPan() {
      this.isPanning = false;
    },
    preventDefault(event) {
      event.preventDefault();
    },
    drawGrid() {
      if (!this.$refs.image || !this.$refs.image.complete) return;
      

      const img = this.$refs.image;
      const canvas = this.$refs.gridCanvas;
      const ctx = canvas.getContext('2d');
      // Set smoothing to false to prevent blurry lines
      ctx.imageSmoothingEnabled = false;
      
      // Set canvas size to match image
      canvas.width = img.width;
      canvas.height = img.height;
      
      // Clear canvas
      ctx.clearRect(0, 0, canvas.width, canvas.height);
      
      // Calculate grid size and number of cells
      const gridSize = img.width / this.pixelWidth;
      const numCellsX = Math.floor(img.width / gridSize);
      const numCellsY = Math.floor(img.height / gridSize);

      // Draw vertical lines
      for (let i = 0; i <= numCellsX; i++) {
        const x = i * gridSize;
        ctx.beginPath();
        ctx.strokeStyle = i % 10 === 0 ? '#FF0000' : '#666666';
        ctx.lineWidth = i % 10 === 0 ? 2 : 0.5;
        ctx.moveTo(Math.round(x), 0);
        ctx.lineTo(Math.round(x), img.height);
        ctx.stroke();

        // Add column numbers for every 10th line
        if (i % 10 === 0) {
          ctx.fillStyle = '#FF0000';
          ctx.font = '12px Arial';
          ctx.fillText(i.toString(), Math.round(x) + 2, 12);
        }
      }
      
      // Draw horizontal lines
      for (let i = 0; i <= numCellsY; i++) {
        const y = i * gridSize;
        ctx.beginPath();
        ctx.strokeStyle = i % 10 === 0 ? '#FF0000' : '#666666';
        ctx.lineWidth = i % 10 === 0 ? 2 : 0.5;
        ctx.moveTo(0, Math.round(y));
        ctx.lineTo(img.width, Math.round(y));
        ctx.stroke();
        // log y and i
        console.log("y, i", y, i);
        // Add row numbers for every 10th line
        if (i % 10 === 0) {
          ctx.fillStyle = '#FF0000';
          ctx.font = '12px Arial';
          ctx.fillText(i.toString(), 2, Math.round(y) + 12);
        }
      }
    }
  },
  mounted() {
    window.addEventListener('resize', this.drawGrid);
  },
  beforeUnmount() {
    window.removeEventListener('resize', this.drawGrid);
  }
}
</script>

<style scoped>
.visualization-container {
  width: 100%;
  height: 80vh;
  overflow: hidden;
  position: relative;
  border: 1px solid #333;
  cursor: move;
}

.canvas-container {
  position: relative;
  display: inline-block;
}

canvas {
  position: absolute;
  top: 0;
  left: 0;
  pointer-events: none;
}

.grid-image {
  display: block;
  max-width: none;
  image-rendering: pixelated;  /* Modern browsers */
  image-rendering: -moz-crisp-edges;  /* Firefox */
  image-rendering: crisp-edges;  /* Safari */
}

.reset-container {
  position: relative;
}
.max-zoom-container {
  position: relative;
}
</style>
