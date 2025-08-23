from ..whisper_db import WhisperDB
import requests
from .wx_auth_client import WXAuthClient
import logging

class WXStoreClient:
    def __init__(self):
        self.auth = WXAuthClient(appid="wx99c7fd9e318b8575", secret="39de4d2977a6caf6763433bfd2a3b3b2")

    def getOrderInfo(
            self, 
            order_id: str
        ) -> dict:
        """
        获取订单信息
        :param order_id: 订单ID
        :return: 订单信息字典
        """

        access_token = self.auth.get_access_token()
        url = f"https://api.weixin.qq.com/channels/ec/order/get?access_token={access_token}"

        payload = {
            "order_id": order_id,
        }
        try:
            resp = requests.post(url, json=payload, timeout=10)
            resp.raise_for_status()
        except Exception as e:
            logging.exception("请求微信订单信息接口失败: %s", e)
            raise

        body = resp.json()
        # 检查企业微信返回的 errcode
        if int(body.get("errcode", -1)) != 0:
            raise RuntimeError(f"微信接口返回错误: errcode={body.get('errcode')}, errmsg={body.get('errmsg')}, body={body}")

        order_info = body.get("order", {})
        if not order_info:
            raise ValueError(f"未找到 order_id={order_id} 的订单信息")
        
        # 处理订单信息，确保返回的字典格式正确
        if isinstance(order_info, dict):
            status_map = {
                10: "待付款",
                12: "礼物待收下",
                13: "凑单买凑团中",
                20: "待发货",
                21: "部分发货",
                30: "待收货",
                100: "完成",
                200: "全部商品售后之后，订单取消",
                250: "未付款用户主动取消或超时未付款订单自动取消"
            }
            ext_info = order_info.get("order_detail", {}).get("ext_info", {})
            filtered_ext_info = {
                "customer_notes": ext_info.get("customer_notes", ""),
                "merchant_notes": ext_info.get("merchant_notes", "")
            }
            delivery_info = order_info.get("order_detail", {}).get("delivery_info", {})
            filtered_delivery_info = {
                "address_info": delivery_info.get("address_info", {}),
                "delivery_product_info": delivery_info.get("delivery_product_info", [])
            }
            new_order_info = {
                "order_id": order_info.get("order_id", ""),
                "create_time": order_info.get("create_time", ""),
                "status": status_map.get(order_info.get("status", ""), "未知状态"),
                "order_detail": {
                    "product_infos": [
                        {
                            "product_id": p.get("product_id", ""),
                            "sale_price": p.get("sale_price", ""),
                            "sku_cnt": p.get("sku_cnt", ""),
                            "title": p.get("title", ""),
                            "on_aftersale_sku_cnt": p.get("on_aftersale_sku_cnt", ""),
                            "finish_aftersale_sku_cnt": p.get("finish_aftersale_sku_cnt", ""),
                            "market_price": p.get("market_price", ""),
                            "sku_attrs": p.get("sku_attrs", [])
                        }
                        for p in order_info.get("order_detail", {}).get("product_infos", [])
                        if isinstance(p, dict)
                    ],
                    "delivery_info": filtered_delivery_info,
                    "ext_info": filtered_ext_info
                }
            }
        elif not isinstance(order_info, dict):
            raise TypeError("订单信息格式错误，应该是字典或列表")

        return new_order_info