-- Databricks notebook source
REVOKE USE SCHEMA ON SCHEMA catalog_prod.bronze FROM bi_power_users;
REVOKE SELECT ON SCHEMA catalog_prod.bronze FROM bi_power_users;