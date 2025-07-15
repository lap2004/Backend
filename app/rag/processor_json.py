import json
from uuid import uuid4
from typing import List

def load_json_chunks(path: str, source: str) -> List[dict]:
    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)

    chunks = []
    for item in data:
        base_title = item.get("title", "")
        ma_nganh = item.get("ma_nganh")
        doi_tuong = item.get("doi_tuong")
        type_ = item.get("type", "")
        title_raw = base_title

        for field, value in item.items():
            if field in {"id", "type", "title", "doi_tuong"} or not value:
                continue

            if field == "diem_chuan_2024" and isinstance(value, str):
                parts = value.split(",")
                for p in parts:
                    p = p.strip()
                    if ":" not in p:
                        continue
                    method, score = p.split(":")
                    method = method.strip()
                    score = score.strip()

                    method_map = {
                        "hoc_ba": "Xét học bạ",
                        "thi_tot_nghiep": "Thi tốt nghiệp THPT",
                        "dgnl_qg": "Đánh giá năng lực"
                    }
                    method_vi = method_map.get(method, method)

                    title = f"Điểm chuẩn 2024 – {method_vi} – {base_title}"
                    content = f"Điểm chuẩn 2024 theo {method_vi} của {base_title} là {score} điểm."

                    chunks.append({
                        "id": uuid4(),
                        "title": title,
                        "title_raw": title_raw,
                        "content": content,
                        "type": type_,
                        "field": field,
                        "source": source,
                        "ma_nganh": ma_nganh,
                        "doi_tuong": doi_tuong,
                        "chunk_index": 0,
                    })
            elif field == "to_hop_xet_tuyen":
                if isinstance(value, list):
                    grouped = "\n".join([f"- {v.strip()}" for v in value if v.strip()])
                    content = f"Các tổ hợp môn xét tuyển cho ngành {base_title} gồm:\n{grouped}"
                else:
                    content = f"Các tổ hợp môn xét tuyển cho ngành {base_title} là:\n- {str(value).strip()}"

                if content:
                    chunks.append({
            "id": uuid4(),
            "title": f"Tổ hợp môn xét tuyển – {base_title}",
            "title_raw": title_raw,
            "content": content,
            "type": type_,
            "field": field,
            "source": source,
            "ma_nganh": ma_nganh,
            "doi_tuong": doi_tuong,
            "chunk_index": 0
        })

            elif field == "ma_nganh":
                content = str(value).strip()
                if content:
                    chunks.append({
                        "id": uuid4(),
                        "title": f"Mã ngành – {base_title}",
                        "title_raw": title_raw,
                        "content": f"Mã ngành của ngành {base_title} là {content}.",
                        "type": type_,
                        "field": field,
                        "source": source,
                        "ma_nganh": content,
                        "doi_tuong": doi_tuong,
                        "chunk_index": 0,
                    })

            else:
                if isinstance(value, dict):
                    content = "\n".join([f"{k.replace('_', ' ')}: {v}" for k, v in value.items()])
                elif isinstance(value, list):
                    content = "\n".join(map(str, value))
                else:
                    content = str(value)

                chunks.append({
                    "id": uuid4(),
                    "title": f"{field} – {base_title}",
                    "title_raw": title_raw,
                    "content": content.strip(),
                    "type": type_,
                    "field": field,
                    "source": source,
                    "ma_nganh": ma_nganh,
                    "doi_tuong": doi_tuong,
                    "chunk_index": 0,
                })

    print(f"Tạo {len(chunks)} đoạn từ {len(data)} bản ghi gốc.")
    return chunks
