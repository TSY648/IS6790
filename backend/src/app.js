import express from "express";
import cors from "cors";

import levelRoutes from "./routes/levelRoutes.js";
import progressRoutes from "./routes/progressRoutes.js";
import resultRoutes from "./routes/resultRoutes.js";
import certificateRoutes from "./routes/certificateRoutes.js";
import { errorHandler } from "./middlewares/errorHandler.js";

const app = express();

app.use(cors());
app.use(express.json());

app.get("/api/health", (req, res) => {
  res.json({ success: true, message: "Server is running" });
});

app.use("/api/levels", levelRoutes);
app.use("/api/progress", progressRoutes);
app.use("/api/results", resultRoutes);
app.use("/api/certificate", certificateRoutes);

app.use(errorHandler);

export default app;
