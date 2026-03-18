import { Router } from "express";
import { getLevel, listLevels } from "../controllers/levelController.js";

const router = Router();

router.get("/", listLevels);
router.get("/:levelId", getLevel);

export default router;
