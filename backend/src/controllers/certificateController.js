import { getCertificateByUserId } from "../services/certificateService.js";

export async function fetchCertificate(req, res, next) {
  try {
    const data = await getCertificateByUserId(req.params.userId);
    res.json({ success: true, data });
  } catch (error) {
    next(error);
  }
}
