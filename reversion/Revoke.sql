-- Databricks notebook source
REVOKE USE CATALOG ON CATALOG demo_catalog FROM `Dvelopers`;
REVOKE USE SCHEMA ON SCHEMA catalog_prod.bronze FROM `Dvelopers