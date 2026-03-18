import { Router } from "express";
import { fetchCertificate } from "../controllers/certificateController.js";

const router = Router();

router.get("/:userId", fetchCertificate);

export default router;
