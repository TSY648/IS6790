import { Router } from "express";
import { fetchProgress, upsertProgress } from "../controllers/progressController.js";

const router = Router();

router.get("/:userId", fetchProgress);
router.post("/", upsertProgress);

export default router;
