import { Router } from "express";
import { createResult } from "../controllers/resultController.js";

const router = Router();

router.post("/", createResult);

export default router;
